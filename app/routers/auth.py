from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from app.database import get_db
from app.models.user import User, Invitation
from app.models.course import Course, Enrollment
from app.models.audit import AuditLog
from app.schemas.auth import (
    LoginRequest,
    TokenResponse,
    UserMeResponse,
    ValidateInviteResponse,
    ActivateAccountRequest
)
from app.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    get_current_active_user
)

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    """
    Authenticate user using email and password.
    Returns signed JWT access token.
    Public self-registration is strictly disallowed.
    """
    user = db.query(User).filter(User.email == payload.email.lower().strip()).first()
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account has been deactivated. Please contact your training administrator."
        )

    # Log successful login
    audit = AuditLog(user_id=user.id, action="LOGIN", details=f"User {user.email} signed in successfully")
    db.add(audit)
    db.commit()

    token = create_access_token(data={"sub": str(user.id), "email": user.email, "role": user.role})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": user
    }

@router.get("/me", response_model=UserMeResponse)
def get_me(current_user: User = Depends(get_current_active_user)):
    """Return currently authenticated user information."""
    return current_user

@router.post("/logout")
def logout(current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    """Audit log user logout."""
    audit = AuditLog(user_id=current_user.id, action="LOGOUT", details=f"User {current_user.email} signed out")
    db.add(audit)
    db.commit()
    return {"message": "Logged out successfully"}

@router.get("/validate-invite", response_model=ValidateInviteResponse)
def validate_invite(token: str = Query(...), db: Session = Depends(get_db)):
    """Validate whether an invitation token is valid, unused, and not expired."""
    invitation = db.query(Invitation).filter(Invitation.token == token).first()
    if not invitation:
        return {"is_valid": False, "message": "Invalid invitation link."}

    if invitation.is_used:
        return {"is_valid": False, "message": "This invitation link has already been used."}

    # Compare UTC timestamps
    now = datetime.now(timezone.utc)
    # Ensure expires_at has timezone
    expires_at = invitation.expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)

    if now > expires_at:
        return {"is_valid": False, "message": "This invitation link has expired. Request a new one from your administrator."}

    user = db.query(User).filter(User.id == invitation.user_id).first()
    if not user:
        return {"is_valid": False, "message": "Associated user account not found."}

    return {
        "is_valid": True,
        "email": user.email,
        "full_name": user.full_name,
        "course_track": invitation.course_track,
        "message": "Invitation is valid."
    }

@router.post("/activate", response_model=TokenResponse)
def activate_account(payload: ActivateAccountRequest, db: Session = Depends(get_db)):
    """
    Activate learner account by setting password via single-use invitation token.
    Enrolls the learner in their assigned course track.
    Returns JWT access token.
    """
    invitation = db.query(Invitation).filter(Invitation.token == payload.token).first()
    if not invitation:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid invitation token.")

    if invitation.is_used:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invitation token has already been redeemed.")

    now = datetime.now(timezone.utc)
    expires_at = invitation.expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)

    if now > expires_at:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invitation token has expired.")

    user = db.query(User).filter(User.id == invitation.user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User account not found.")

    # Set new password & mark active
    user.hashed_password = get_password_hash(payload.password)
    user.is_active = True
    invitation.is_used = True

    # Ensure learner is enrolled in the assigned track
    course = db.query(Course).filter(Course.track_name == invitation.course_track).first()
    if course:
        existing_enrollment = db.query(Enrollment).filter(
            Enrollment.user_id == user.id,
            Enrollment.course_id == course.id
        ).first()
        if not existing_enrollment:
            enrollment = Enrollment(user_id=user.id, course_id=course.id)
            db.add(enrollment)

    audit = AuditLog(
        user_id=user.id,
        action="ACCOUNT_ACTIVATED",
        details=f"Learner {user.email} successfully activated account with track '{invitation.course_track}'"
    )
    db.add(audit)
    db.commit()
    db.refresh(user)

    token = create_access_token(data={"sub": str(user.id), "email": user.email, "role": user.role})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": user
    }
