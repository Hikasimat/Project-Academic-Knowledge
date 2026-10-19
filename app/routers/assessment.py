from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from typing import List, Optional
import json

from app.database import get_db
from app.models.user import User
from app.models.course import Course, CourseStep, Enrollment, StepProgress
from app.models.assessment import ExamAttempt
from app.models.audit import AuditLog
from app.assessment_data import (
    ASSESSMENT_QUESTIONS,
    PASSING_THRESHOLD_PERCENT,
    TOTAL_QUESTIONS
)
from app.schemas.assessment import (
    QuestionOut,
    ExamSubmitRequest,
    ExamResultOut,
    ExamAttemptOut
)
from app.security import get_current_active_user

router = APIRouter(prefix="/api/assessment", tags=["Assessment Integrity"])

@router.get("/questions", response_model=List[QuestionOut])
def get_exam_questions(current_user: User = Depends(get_current_active_user)):
    """
    Serve the 10 authoritative assessment questions.
    SECURITY REQUIREMENT: Correct answers and answer keys are never sent to the client.
    """
    return [
        QuestionOut(
            id=q["id"],
            question=q["question"],
            options=q["options"]
        )
        for q in ASSESSMENT_QUESTIONS
    ]

@router.post("/submit", response_model=ExamResultOut)
def submit_exam(
    payload: ExamSubmitRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Submit examination answers for server-side grading.
    Verifies full course completion before accepting examination submission.
    Calculates exact score, records attempt in database, and enforces 80% passing threshold.
    """
    course = db.query(Course).filter(Course.id == payload.course_id).first()
    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found.")

    enrollment = db.query(Enrollment).filter(
        Enrollment.user_id == current_user.id,
        Enrollment.course_id == course.id
    ).first()

    if not enrollment and current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not enrolled in this course.")

    # Verify all 15 course steps are completed before exam submission
    total_steps = db.query(CourseStep).filter(CourseStep.course_id == course.id).count()
    completed_steps = db.query(StepProgress).filter(StepProgress.enrollment_id == enrollment.id).count() if enrollment else 0

    if completed_steps < total_steps and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Exam locked: You must complete all {total_steps} course steps before taking the final exam (current progress: {completed_steps}/{total_steps})."
        )

    # Server-side authoritative grading
    q_map = {q["id"]: q["correct_index"] for q in ASSESSMENT_QUESTIONS}
    correct_count = 0
    submitted_answers_dict = {}

    for ans in payload.answers:
        submitted_answers_dict[ans.question_id] = ans.selected_option
        if ans.question_id in q_map and ans.selected_option == q_map[ans.question_id]:
            correct_count += 1

    percentage = round((correct_count / TOTAL_QUESTIONS) * 100.0, 1)
    passed = percentage >= PASSING_THRESHOLD_PERCENT

    # Count prior attempts
    prior_attempts = db.query(ExamAttempt).filter(
        ExamAttempt.user_id == current_user.id,
        ExamAttempt.course_id == course.id
    ).count()

    attempt_record = ExamAttempt(
        user_id=current_user.id,
        course_id=course.id,
        attempt_number=prior_attempts + 1,
        score=correct_count,
        total_questions=TOTAL_QUESTIONS,
        percentage=percentage,
        passed=passed,
        answers_json=json.dumps(submitted_answers_dict)
    )
    db.add(attempt_record)

    audit = AuditLog(
        user_id=current_user.id,
        action="EXAM_SUBMISSION",
        details=f"User {current_user.email} completed exam attempt #{prior_attempts + 1}: {correct_count}/{TOTAL_QUESTIONS} ({percentage}%), Passed={passed}"
    )
    db.add(audit)
    db.commit()
    db.refresh(attempt_record)

    certificate_eligible = passed and (completed_steps >= total_steps or current_user.role == "admin")

    msg = (
        "Congratulations! You passed the Plus UAE × Vortexen Knowledge Assessment."
        if passed
        else f"Score {correct_count}/{TOTAL_QUESTIONS} ({percentage}%). Passing requires at least {PASSING_THRESHOLD_PERCENT}%. Please review the training material and try again."
    )

    return ExamResultOut(
        score=correct_count,
        total_questions=TOTAL_QUESTIONS,
        percentage=percentage,
        passed=passed,
        attempt_number=attempt_record.attempt_number,
        certificate_eligible=certificate_eligible,
        message=msg
    )

@router.get("/my-attempts", response_model=List[ExamAttemptOut])
def get_my_exam_attempts(
    course_id: int = Query(...),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Retrieve history of current user's exam attempts for this course."""
    attempts = db.query(ExamAttempt).filter(
        ExamAttempt.user_id == current_user.id,
        ExamAttempt.course_id == course_id
    ).order_by(ExamAttempt.created_at.desc()).all()
    return attempts
