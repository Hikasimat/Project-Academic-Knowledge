import pytest
from app.models.course import Course, CourseStep, Enrollment, StepProgress
from app.assessment_data import ASSESSMENT_QUESTIONS

def test_questions_strip_answers(client, learner_token):
    """Verify assessment questions never expose correct answers to client."""
    res = client.get("/api/assessment/questions", headers={"Authorization": f"Bearer {learner_token}"})
    assert res.status_code == 200
    questions = res.json()
    assert len(questions) == 10
    for q in questions:
        assert "correct_index" not in q
        assert "rationale" not in q
        assert len(q["options"]) >= 3

def test_exam_locked_until_all_steps_complete(client, db, learner_user, learner_token):
    """Verify exam submission is blocked before all 15 steps are completed."""
    course = db.query(Course).first()
    enrollment = Enrollment(user_id=learner_user.id, course_id=course.id)
    db.add(enrollment)
    db.flush()

    # Complete only step 1
    step1 = db.query(CourseStep).filter(CourseStep.course_id == course.id, CourseStep.step_number == 1).first()
    db.add(StepProgress(enrollment_id=enrollment.id, step_id=step1.id))
    db.commit()

    # Attempt to submit exam
    submit_res = client.post("/api/assessment/submit", headers={"Authorization": f"Bearer {learner_token}"}, json={
        "course_id": course.id,
        "answers": [{"question_id": 1, "selected_option": 1}]
    })
    assert submit_res.status_code == 400
    assert "Exam locked" in submit_res.json()["detail"]

def test_exam_grading_8_passes_7_fails(client, db, learner_user, learner_token):
    """Verify 8/10 passes (>=80%) and 7/10 fails (<80%)."""
    course = db.query(Course).first()
    enrollment = Enrollment(user_id=learner_user.id, course_id=course.id, is_completed=True)
    db.add(enrollment)
    db.flush()

    # Add all 15 steps progress
    steps = db.query(CourseStep).filter(CourseStep.course_id == course.id).all()
    for s in steps:
        db.add(StepProgress(enrollment_id=enrollment.id, step_id=s.id))
    db.commit()

    # 1. Submit with 7 correct answers (FAIL)
    fail_answers = []
    for idx, q in enumerate(ASSESSMENT_QUESTIONS):
        if idx < 7:
            fail_answers.append({"question_id": q["id"], "selected_option": q["correct_index"]})
        else:
            wrong_opt = (q["correct_index"] + 1) % len(q["options"])
            fail_answers.append({"question_id": q["id"], "selected_option": wrong_opt})

    res_fail = client.post("/api/assessment/submit", headers={"Authorization": f"Bearer {learner_token}"}, json={
        "course_id": course.id,
        "answers": fail_answers
    })
    assert res_fail.status_code == 200
    fail_data = res_fail.json()
    assert fail_data["score"] == 7
    assert fail_data["percentage"] == 70.0
    assert fail_data["passed"] is False
    assert fail_data["certificate_eligible"] is False
    assert fail_data["attempt_number"] == 1

    # 2. Retake test with 8 correct answers (PASS)
    pass_answers = []
    for idx, q in enumerate(ASSESSMENT_QUESTIONS):
        if idx < 8:
            pass_answers.append({"question_id": q["id"], "selected_option": q["correct_index"]})
        else:
            wrong_opt = (q["correct_index"] + 1) % len(q["options"])
            pass_answers.append({"question_id": q["id"], "selected_option": wrong_opt})

    res_pass = client.post("/api/assessment/submit", headers={"Authorization": f"Bearer {learner_token}"}, json={
        "course_id": course.id,
        "answers": pass_answers
    })
    assert res_pass.status_code == 200
    pass_data = res_pass.json()
    assert pass_data["score"] == 8
    assert pass_data["percentage"] == 80.0
    assert pass_data["passed"] is True
    assert pass_data["certificate_eligible"] is True
    assert pass_data["attempt_number"] == 2
