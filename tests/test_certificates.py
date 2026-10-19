import pytest
from app.models.course import Course, CourseStep, Enrollment, StepProgress
from app.models.assessment import ExamAttempt
from app.models.certificate import Certificate

def test_certificate_eligibility_and_issuance(client, db, learner_user, learner_token):
    """
    Verify complete certificate workflow:
    1. Ineligible initially.
    2. Eligible only when 15 steps are completed AND exam >= 80%.
    3. Idempotent issuance (no duplicate certificates).
    4. Public verification confirms authenticity.
    5. PDF export returns valid binary.
    """
    course = db.query(Course).first()
    enrollment = Enrollment(user_id=learner_user.id, course_id=course.id)
    db.add(enrollment)
    db.commit()

    # 1. Initially ineligible
    el_res = client.get(f"/api/certificates/eligibility?course_id={course.id}", headers={"Authorization": f"Bearer {learner_token}"})
    assert el_res.status_code == 200
    assert el_res.json()["eligible"] is False

    # Attempt to issue must fail
    issue_fail = client.post(f"/api/certificates/issue?course_id={course.id}", headers={"Authorization": f"Bearer {learner_token}"})
    assert issue_fail.status_code == 400

    # 2. Complete all 15 steps
    steps = db.query(CourseStep).filter(CourseStep.course_id == course.id).all()
    for s in steps:
        db.add(StepProgress(enrollment_id=enrollment.id, step_id=s.id))
    enrollment.is_completed = True
    db.commit()

    # Still ineligible without passing exam
    el_res2 = client.get(f"/api/certificates/eligibility?course_id={course.id}", headers={"Authorization": f"Bearer {learner_token}"})
    assert el_res2.json()["steps_completed"] is True
    assert el_res2.json()["exam_passed"] is False
    assert el_res2.json()["eligible"] is False

    # Record passing exam (85%)
    attempt = ExamAttempt(
        user_id=learner_user.id,
        course_id=course.id,
        attempt_number=1,
        score=9,
        total_questions=10,
        percentage=90.0,
        passed=True
    )
    db.add(attempt)
    db.commit()

    # Now eligible!
    el_res3 = client.get(f"/api/certificates/eligibility?course_id={course.id}", headers={"Authorization": f"Bearer {learner_token}"})
    assert el_res3.json()["eligible"] is True

    # 3. Issue certificate
    issue_res = client.post(f"/api/certificates/issue?course_id={course.id}", headers={"Authorization": f"Bearer {learner_token}"})
    assert issue_res.status_code == 200
    cert_data = issue_res.json()
    code = cert_data["certificate_code"]
    assert code.startswith("PUVX-2026-")
    assert cert_data["learner_name"] == learner_user.full_name
    assert cert_data["course_track"] == course.track_name

    # 4. Repeat issuance (Idempotency test)
    repeat_res = client.post(f"/api/certificates/issue?course_id={course.id}", headers={"Authorization": f"Bearer {learner_token}"})
    assert repeat_res.status_code == 200
    assert repeat_res.json()["certificate_code"] == code

    # Verify only one certificate was inserted in DB
    certs_in_db = db.query(Certificate).filter(
        Certificate.user_id == learner_user.id,
        Certificate.course_id == course.id
    ).count()
    assert certs_in_db == 1

    # 5. Public verification endpoint
    verify_res = client.get(f"/api/certificates/verify/{code}")
    assert verify_res.status_code == 200
    v_data = verify_res.json()
    assert v_data["is_valid"] is True
    assert v_data["certificate_code"] == code
    assert v_data["learner_name"] == learner_user.full_name
    assert v_data["status"] == "AUTHENTIC_AND_VALID"
    assert "Does not constitute external accreditation" in v_data["disclaimer"]

    # 6. Verify non-existent code
    fake_verify = client.get("/api/certificates/verify/PUVX-FAKE-0000-0000")
    assert fake_verify.json()["is_valid"] is False
    assert fake_verify.json()["status"] == "NOT_FOUND"

    # 7. PDF download
    pdf_res = client.get(f"/api/certificates/{code}/pdf")
    assert pdf_res.status_code == 200
    assert pdf_res.headers["content-type"] == "application/pdf"
    assert len(pdf_res.content) > 1000
    assert pdf_res.content.startswith(b"%PDF")
