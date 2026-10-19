import pytest
from app.models.course import Course, CourseStep, Enrollment, StepProgress
from app.models.assessment import ExamAttempt
from app.models.certificate import Certificate
from app.assessment_data import ASSESSMENT_QUESTIONS

def test_full_acceptance_criteria_e2e_workflow(client, admin_user):
    """
    Test the complete 13-step acceptance workflow end to end:
    1. Administrator securely signs in.
    2. Administrator creates a learner account and assigns course track.
    3. Administrator hands the learner a secure activation invitation.
    4. Learner activates account and logs in.
    5. Learner sees assigned course and completes steps in required sequential order.
    6. Application saves progress in backend database.
    7. Final exam unlocks after all required steps completed.
    8. Learner takes the existing 10-question test.
    9. Backend grades test and verifies course completion.
    10. Learner receives persistent certificate automatically.
    11. Learner can view, print, and download PDF certificate.
    12. Certificate identifier can be verified publicly.
    13. Administrator reviews learner's progress, exam result, and certificate status.
    """
    # Step 1: Administrator securely signs in
    admin_login_res = client.post("/api/auth/login", json={
        "email": admin_user.email,
        "password": "AdminPass123!"
    })
    assert admin_login_res.status_code == 200
    admin_token = admin_login_res.json()["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    # Step 2 & 3: Administrator creates learner account and receives invitation link
    create_res = client.post("/api/admin/learners", headers=admin_headers, json={
        "full_name": "Noura Al-Zaabi",
        "email": "noura.alzaabi@plusuae.com",
        "course_track": "Plus UAE — Sales"
    })
    assert create_res.status_code == 200
    invite_data = create_res.json()
    token = invite_data["invitation_token"]
    assert token is not None
    assert "/?invite=" in invite_data["invitation_url"]

    # Step 4: Learner validates invitation and activates account
    val_res = client.get(f"/api/auth/validate-invite?token={token}")
    assert val_res.status_code == 200
    assert val_res.json()["is_valid"] is True
    assert val_res.json()["course_track"] == "Plus UAE — Sales"

    act_res = client.post("/api/auth/activate", json={
        "token": token,
        "password": "NouraPassSecure2026!"
    })
    assert act_res.status_code == 200
    learner_token = act_res.json()["access_token"]
    learner_headers = {"Authorization": f"Bearer {learner_token}"}

    # Step 5 & 6: Learner views assigned course and completes 15 steps sequentially
    my_courses_res = client.get("/api/courses/my-courses", headers=learner_headers)
    assert my_courses_res.status_code == 200
    courses = my_courses_res.json()
    assert len(courses) >= 1
    target_course = next(c for c in courses if c["track_name"] == "Plus UAE — Sales")
    course_id = target_course["id"]

    # Verify initial progression state
    course_detail_res = client.get(f"/api/courses/{course_id}", headers=learner_headers)
    assert course_detail_res.status_code == 200
    steps = course_detail_res.json()["steps"]
    assert len(steps) == 15
    assert steps[0]["is_unlocked"] is True
    assert steps[1]["is_unlocked"] is False

    # Attempt out-of-order completion (must fail)
    step2_fail = client.post(
        f"/api/courses/{course_id}/steps/{steps[1]['id']}/complete",
        headers=learner_headers
    )
    assert step2_fail.status_code == 400

    # Complete all 15 steps in order
    for idx, s in enumerate(steps):
        step_res = client.post(
            f"/api/courses/{course_id}/steps/{s['id']}/complete",
            headers=learner_headers
        )
        assert step_res.status_code == 200
        assert step_res.json()["completed_steps"] == idx + 1

    # Step 7: Final exam unlocks after all 15 steps completed
    progress_check = client.get(f"/api/courses/{course_id}", headers=learner_headers)
    assert progress_check.json()["completed_steps"] == 15
    assert progress_check.json()["exam_eligible"] is True

    # Step 8 & 9: Learner takes 10-question test and backend grades it
    exam_questions_res = client.get("/api/assessment/questions", headers=learner_headers)
    assert exam_questions_res.status_code == 200
    questions = exam_questions_res.json()
    assert len(questions) == 10

    # Answer 9 of 10 correctly (90%)
    answers = []
    for idx, q in enumerate(ASSESSMENT_QUESTIONS):
        if idx < 9:
            answers.append({"question_id": q["id"], "selected_option": q["correct_index"]})
        else:
            wrong_opt = (q["correct_index"] + 1) % len(q["options"])
            answers.append({"question_id": q["id"], "selected_option": wrong_opt})

    submit_exam_res = client.post("/api/assessment/submit", headers=learner_headers, json={
        "course_id": course_id,
        "answers": answers
    })
    assert submit_exam_res.status_code == 200
    exam_result = submit_exam_res.json()
    assert exam_result["score"] == 9
    assert exam_result["percentage"] == 90.0
    assert exam_result["passed"] is True
    assert exam_result["certificate_eligible"] is True

    # Step 10: Automatic persistent certificate issuance
    # First check eligibility
    eligibility_res = client.get(f"/api/certificates/eligibility?course_id={course_id}", headers=learner_headers)
    assert eligibility_res.status_code == 200
    assert eligibility_res.json()["eligible"] is True

    # Issue certificate
    issue_res = client.post(f"/api/certificates/issue?course_id={course_id}", headers=learner_headers)
    assert issue_res.status_code == 200
    cert = issue_res.json()
    cert_code = cert["certificate_code"]
    assert cert_code.startswith("PUVX-2026-")
    assert cert["learner_name"] == "Noura Al-Zaabi"
    assert cert["course_track"] == "Plus UAE — Sales"

    # Step 11: Download PDF certificate
    pdf_res = client.get(f"/api/certificates/{cert_code}/pdf")
    assert pdf_res.status_code == 200
    assert pdf_res.headers["content-type"] == "application/pdf"
    assert len(pdf_res.content) > 500

    # Step 12: Certificate identifier can be verified publicly
    verify_res = client.get(f"/api/certificates/verify/{cert_code}")
    assert verify_res.status_code == 200
    v_data = verify_res.json()
    assert v_data["is_valid"] is True
    assert v_data["learner_name"] == "Noura Al-Zaabi"
    assert v_data["course_track"] == "Plus UAE — Sales"
    assert v_data["status"] == "AUTHENTIC_AND_VALID"

    # Step 13: Administrator reviews learner's progress, exam results, and certificate status
    admin_list_res = client.get("/api/admin/learners", headers=admin_headers)
    assert admin_list_res.status_code == 200
    all_learners = admin_list_res.json()
    target_learner = next(l for l in all_learners if l["email"] == "noura.alzaabi@plusuae.com")
    assert target_learner["full_name"] == "Noura Al-Zaabi"
    assert target_learner["is_active"] is True
    assert len(target_learner["courses"]) >= 1
    c_info = target_learner["courses"][0]
    assert c_info["completed_steps"] == 15
    assert c_info["progress_percentage"] == 100.0
    assert c_info["exam_score"] == 9
    assert c_info["exam_passed"] is True
    assert c_info["certificate_code"] == cert_code
