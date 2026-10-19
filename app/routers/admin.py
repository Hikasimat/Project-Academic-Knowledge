from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone
from typing import List
import secrets

from app.database import get_db
from app.config import settings
from app.models.user import User, Invitation
from app.models.course import Course, CourseStep, Enrollment, StepProgress
from app.models.assessment import ExamAttempt
from app.models.certificate import Certificate
from app.models.service_lesson import ServiceLesson
from app.models.audit import AuditLog
from app.schemas.admin import (
    LearnerCreateRequest,
    LearnerCreateResponse,
    LearnerListItem,
    LearnerProgressDetail,
    UserStatusUpdateRequest,
    ResetInviteResponse
)
from app.schemas.service_lesson import ServiceLessonCreate, ServiceLessonOut
from app.security import require_admin, generate_invitation_token, get_password_hash

router = APIRouter(prefix="/api/admin", tags=["Administration"])

@router.post("/learners", response_model=LearnerCreateResponse)
def create_learner(
    payload: LearnerCreateRequest,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """
    Create a new learner account.
    Generates a secure single-use invitation token with expiration.
    Assigns the learner to the specified course track.
    """
    email_clean = payload.email.lower().strip()
    existing_user = db.query(User).filter(User.email == email_clean).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email address already exists."
        )

    # Validate course track
    course = db.query(Course).filter(Course.track_name == payload.course_track).first()
    if not course:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Course track '{payload.course_track}' does not exist."
        )

    # Generate temporary un-guessable hash for unactivated account
    temp_hash = get_password_hash(secrets.token_urlsafe(32))
    new_user = User(
        email=email_clean,
        full_name=payload.full_name.strip(),
        hashed_password=temp_hash,
        role="learner",
        is_active=True
    )
    db.add(new_user)
    db.flush()

    # Create enrollment
    enrollment = Enrollment(user_id=new_user.id, course_id=course.id)
    db.add(enrollment)

    # Create expiring single-use invitation
    token = generate_invitation_token()
    expires_at = datetime.now(timezone.utc) + timedelta(hours=settings.INVITATION_EXPIRE_HOURS)
    invitation = Invitation(
        user_id=new_user.id,
        token=token,
        course_track=course.track_name,
        expires_at=expires_at,
        is_used=False
    )
    db.add(invitation)

    # Audit log
    audit = AuditLog(
        user_id=admin.id,
        action="CREATE_LEARNER",
        details=f"Admin {admin.email} created learner {new_user.email} assigned to '{course.track_name}'"
    )
    db.add(audit)
    db.commit()

    invitation_url = f"/?invite={token}"
    return {
        "id": new_user.id,
        "email": new_user.email,
        "full_name": new_user.full_name,
        "course_track": course.track_name,
        "invitation_token": token,
        "invitation_url": invitation_url,
        "expires_at": expires_at
    }

@router.get("/learners", response_model=List[LearnerListItem])
def list_learners(
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """List all registered learners with comprehensive progress, exam, and certification status."""
    learners = db.query(User).filter(User.role == "learner").order_by(User.created_at.desc()).all()
    results = []

    for learner in learners:
        enrollments = db.query(Enrollment).filter(Enrollment.user_id == learner.id).all()
        courses_progress = []

        for enrollment in enrollments:
            course = enrollment.course
            total_steps = db.query(CourseStep).filter(CourseStep.course_id == course.id).count()
            completed_steps = db.query(StepProgress).filter(StepProgress.enrollment_id == enrollment.id).count()
            progress_pct = (completed_steps / total_steps * 100.0) if total_steps > 0 else 0.0

            # Latest exam attempt
            latest_exam = db.query(ExamAttempt).filter(
                ExamAttempt.user_id == learner.id,
                ExamAttempt.course_id == course.id
            ).order_by(ExamAttempt.created_at.desc()).first()

            # Certificate
            cert = db.query(Certificate).filter(
                Certificate.user_id == learner.id,
                Certificate.course_id == course.id
            ).first()

            courses_progress.append(LearnerProgressDetail(
                course_id=course.id,
                course_title=course.title,
                course_track=course.track_name,
                completed_steps=completed_steps,
                total_steps=total_steps,
                progress_percentage=round(progress_pct, 1),
                is_completed=enrollment.is_completed,
                exam_score=latest_exam.score if latest_exam else None,
                exam_passed=latest_exam.passed if latest_exam else False,
                certificate_code=cert.certificate_code if cert else None,
                certificate_issued_at=cert.issue_date if cert else None
            ))

        # Check pending invitation
        pending_invite = db.query(Invitation).filter(
            Invitation.user_id == learner.id,
            Invitation.is_used == False
        ).order_by(Invitation.created_at.desc()).first()

        results.append(LearnerListItem(
            id=learner.id,
            email=learner.email,
            full_name=learner.full_name,
            role=learner.role,
            is_active=learner.is_active,
            created_at=learner.created_at,
            courses=courses_progress,
            invitation_token=pending_invite.token if pending_invite else None,
            invitation_url=f"/?invite={pending_invite.token}" if pending_invite else None
        ))

    return results

@router.put("/learners/{learner_id}/status")
def update_learner_status(
    learner_id: int,
    payload: UserStatusUpdateRequest,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """Activate or deactivate a learner account."""
    learner = db.query(User).filter(User.id == learner_id, User.role == "learner").first()
    if not learner:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Learner not found.")

    learner.is_active = payload.is_active
    audit = AuditLog(
        user_id=admin.id,
        action="UPDATE_LEARNER_STATUS",
        details=f"Admin {admin.email} set active={payload.is_active} for learner {learner.email}"
    )
    db.add(audit)
    db.commit()
    return {"message": f"Learner status updated to {'Active' if payload.is_active else 'Deactivated'}."}

@router.post("/learners/{learner_id}/reset-invite", response_model=ResetInviteResponse)
def reset_invitation(
    learner_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """Generate a fresh single-use activation invitation token."""
    learner = db.query(User).filter(User.id == learner_id, User.role == "learner").first()
    if not learner:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Learner not found.")

    # Invalidate previous unused invitations
    db.query(Invitation).filter(Invitation.user_id == learner.id, Invitation.is_used == False).update({"is_used": True})

    # Find learner track
    enrollment = db.query(Enrollment).filter(Enrollment.user_id == learner.id).first()
    track_name = enrollment.course.track_name if enrollment else "Both companies — Foundation"

    token = generate_invitation_token()
    expires_at = datetime.now(timezone.utc) + timedelta(hours=settings.INVITATION_EXPIRE_HOURS)
    invitation = Invitation(
        user_id=learner.id,
        token=token,
        course_track=track_name,
        expires_at=expires_at,
        is_used=False
    )
    db.add(invitation)

    audit = AuditLog(
        user_id=admin.id,
        action="RESET_INVITATION",
        details=f"Admin {admin.email} generated fresh invitation for {learner.email}"
    )
    db.add(audit)
    db.commit()

    return {
        "invitation_token": token,
        "invitation_url": f"/?invite={token}",
        "expires_at": expires_at
    }

@router.get("/services", response_model=List[ServiceLessonOut])
def list_admin_services(
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """Retrieve all service lessons and administrative drafts."""
    return db.query(ServiceLesson).order_by(ServiceLesson.created_at.desc()).all()

@router.post("/services", response_model=ServiceLessonOut)
def create_admin_service(
    payload: ServiceLessonCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """
    Create a new service lesson draft.
    Restricted to authorized administrators.
    """
    lesson = ServiceLesson(
        company=payload.company,
        name=payload.name.strip(),
        buyer=payload.buyer.strip(),
        dm=payload.dm.strip(),
        process=payload.process.strip(),
        question=payload.question.strip(),
        risk=payload.risk.strip(),
        is_published=True,
        created_by_id=admin.id
    )
    db.add(lesson)
    db.flush()

    audit = AuditLog(
        user_id=admin.id,
        action="CREATE_SERVICE_LESSON",
        details=f"Admin {admin.email} created service lesson '{lesson.name}' for {lesson.company}"
    )
    db.add(audit)
    db.commit()
    db.refresh(lesson)
    return lesson

@router.get("/audit-logs")
def get_audit_logs(
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """Retrieve recent administrative audit logs."""
    logs = db.query(AuditLog).order_by(AuditLog.timestamp.desc()).limit(50).all()
    return [{
        "id": l.id,
        "action": l.action,
        "details": l.details,
        "timestamp": l.timestamp
    } for l in logs]
