from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from typing import List

from app.database import get_db
from app.models.user import User
from app.models.course import Course, CourseStep, Enrollment, StepProgress
from app.models.service_lesson import ServiceLesson
from app.models.audit import AuditLog
from app.schemas.course import (
    CourseOut,
    CourseDetailOut,
    CourseStepOut,
    StepCompleteRequest,
    StepCompleteResponse
)
from app.security import get_current_active_user
from app.course_data import FIFTEEN_DAY_SYLLABUS

router = APIRouter(prefix="/api/courses", tags=["Learning Progression"])

@router.get("/my-courses", response_model=List[CourseOut])
def get_my_courses(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Retrieve all courses the current user is enrolled in.
    Administrators have access to review all courses.
    """
    if current_user.role == "admin":
        courses = db.query(Course).all()
        # Sort so specialized_toolkits is first
        courses.sort(key=lambda c: 0 if c.code == "specialized_toolkits" else 1)
        results = []
        for c in courses:
            total = db.query(CourseStep).filter(CourseStep.course_id == c.id).count()
            results.append(CourseOut(
                id=c.id,
                code=c.code,
                title=c.title,
                track_name=c.track_name,
                description=c.description,
                completed_steps=total,
                total_steps=total,
                progress_percentage=100.0,
                is_completed=True,
                exam_eligible=True
            ))
        return results

    enrollments = db.query(Enrollment).filter(Enrollment.user_id == current_user.id).all()
    if not enrollments:
        master_course = db.query(Course).filter(Course.code == "specialized_toolkits").first()
        if master_course:
            enr = Enrollment(user_id=current_user.id, course_id=master_course.id)
            db.add(enr)
            db.commit()
            enrollments = [enr]
    results = []
    for enr in enrollments:
        c = enr.course
        total = db.query(CourseStep).filter(CourseStep.course_id == c.id).count()
        completed = db.query(StepProgress).filter(StepProgress.enrollment_id == enr.id).count()
        pct = (completed / total * 100.0) if total > 0 else 0.0
        is_completed = (completed >= total) and (total > 0)
        results.append(CourseOut(
            id=c.id,
            code=c.code,
            title=c.title,
            track_name=c.track_name,
            description=c.description,
            completed_steps=completed,
            total_steps=total,
            progress_percentage=round(pct, 1),
            is_completed=is_completed,
            exam_eligible=is_completed
        ))
    return results

@router.get("/{course_id}", response_model=CourseDetailOut)
def get_course_detail(
    course_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Retrieve course details and sequential step state.
    Calculates completed and locked/unlocked state per step.
    """
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found.")

    enrollment = db.query(Enrollment).filter(
        Enrollment.user_id == current_user.id,
        Enrollment.course_id == course.id
    ).first()

    if not enrollment and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not enrolled in this course track."
        )

    steps = db.query(CourseStep).filter(CourseStep.course_id == course.id).order_by(CourseStep.step_number).all()
    completed_step_ids = set()
    if enrollment:
        progress_records = db.query(StepProgress).filter(StepProgress.enrollment_id == enrollment.id).all()
        completed_step_ids = {p.step_id for p in progress_records}

    step_outs = []
    total_steps = len(steps)
    completed_count = len(completed_step_ids)

    # In Coursera sequential progression:
    # Step 1 is always unlocked.
    # Step N is unlocked if Step N-1 is completed.
    prev_completed = True
    for s in steps:
        is_comp = s.id in completed_step_ids or current_user.role == "admin"
        is_unlocked = prev_completed or current_user.role == "admin"

        syllabus_meta = next((item for item in FIFTEEN_DAY_SYLLABUS if item["day_number"] == s.day_number), {})
        step_topics = syllabus_meta.get("topics", [])
        sec_num = getattr(s, "section_number", None) or syllabus_meta.get("section_number", 1)
        sec_title = getattr(s, "section_title", None) or syllabus_meta.get("section_title", "Plus UAE Service Catalog")

        step_outs.append(CourseStepOut(
            id=s.id,
            step_number=s.step_number,
            day_number=s.day_number,
            section_number=sec_num,
            section_title=sec_title,
            title=s.title,
            description=s.description,
            target_section=s.target_section,
            topics=step_topics,
            is_mandatory=s.is_mandatory,
            is_completed=is_comp,
            is_unlocked=is_unlocked,
            completed_at=None
        ))
        prev_completed = is_comp

    pct = (completed_count / total_steps * 100.0) if total_steps > 0 else 0.0
    is_fully_done = (completed_count >= total_steps) and (total_steps > 0)

    return CourseDetailOut(
        id=course.id,
        code=course.code,
        title=course.title,
        track_name=course.track_name,
        description=course.description,
        completed_steps=completed_count,
        total_steps=total_steps,
        progress_percentage=round(pct, 1),
        is_completed=is_fully_done or (enrollment.is_completed if enrollment else False),
        exam_eligible=is_fully_done or (enrollment.is_completed if enrollment else False) or current_user.role == "admin",
        steps=step_outs
    )

@router.post("/{course_id}/steps/{step_id}/complete", response_model=StepCompleteResponse)
def complete_step(
    course_id: int,
    step_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Mark a sequential learning step as completed.
    Enforces strict Coursera-style sequence:
    Step N cannot be completed unless Step N-1 is completed.
    """
    enrollment = db.query(Enrollment).filter(
        Enrollment.user_id == current_user.id,
        Enrollment.course_id == course_id
    ).first()

    if not enrollment:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not enrolled in this course."
        )

    target_step = db.query(CourseStep).filter(
        CourseStep.id == step_id,
        CourseStep.course_id == course_id
    ).first()

    if not target_step:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Step not found in this course.")

    # Check if already completed (idempotent)
    existing_progress = db.query(StepProgress).filter(
        StepProgress.enrollment_id == enrollment.id,
        StepProgress.step_id == target_step.id
    ).first()

    all_steps = db.query(CourseStep).filter(CourseStep.course_id == course_id).order_by(CourseStep.step_number).all()
    total_steps = len(all_steps)

    if not existing_progress:
        # Verify previous step completion
        if target_step.step_number > 1:
            prev_step = next((s for s in all_steps if s.step_number == target_step.step_number - 1), None)
            if prev_step:
                prev_progress = db.query(StepProgress).filter(
                    StepProgress.enrollment_id == enrollment.id,
                    StepProgress.step_id == prev_step.id
                ).first()
                if not prev_progress:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Sequential progression required: Please complete Step {prev_step.step_number} ('{prev_step.title}') first."
                    )

        # Record step completion
        new_progress = StepProgress(enrollment_id=enrollment.id, step_id=target_step.id)
        db.add(new_progress)
        db.flush()

    # Recalculate completed count
    completed_count = db.query(StepProgress).filter(StepProgress.enrollment_id == enrollment.id).count()
    pct = (completed_count / total_steps * 100.0) if total_steps > 0 else 0.0
    exam_eligible = (completed_count >= total_steps) and (total_steps > 0)

    if exam_eligible and not enrollment.is_completed:
        enrollment.is_completed = True
        enrollment.completed_at = datetime.now(timezone.utc)

    db.commit()

    next_step_num = target_step.step_number + 1 if target_step.step_number < total_steps else None

    return StepCompleteResponse(
        success=True,
        message=f"Step {target_step.step_number} completed successfully.",
        step_number=target_step.step_number,
        completed_steps=completed_count,
        total_steps=total_steps,
        progress_percentage=round(pct, 1),
        next_step_unlocked=next_step_num,
        exam_eligible=exam_eligible
    )

@router.get("/published/services")
def get_published_services(db: Session = Depends(get_db)):
    """Retrieve published service updates created by administrators."""
    services = db.query(ServiceLesson).filter(ServiceLesson.is_published == True).order_by(ServiceLesson.created_at.desc()).all()
    return [{
        "id": s.id,
        "company": s.company,
        "name": s.name,
        "buyer": s.buyer,
        "dm": s.dm,
        "process": s.process,
        "question": s.question,
        "risk": s.risk,
        "created_at": s.created_at
    } for s in services]
