from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from datetime import datetime, timezone
import hashlib
import secrets
import io

from app.database import get_db
from app.models.user import User
from app.models.course import Course, CourseStep, Enrollment, StepProgress
from app.models.assessment import ExamAttempt
from app.models.certificate import Certificate
from app.models.audit import AuditLog
from app.schemas.certificate import CertificateOut, CertificateVerifyOut
from app.security import get_current_active_user

from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib import colors
from reportlab.pdfgen import canvas

router = APIRouter(prefix="/api/certificates", tags=["Certificate Issuance & Verification"])

CERTIFICATE_DISCLAIMER = (
    "Self-assessed digital training certificate. Manager verification required for formal internal HR records. "
    "Does not constitute external accreditation or technical authorization."
)

def generate_cert_code() -> str:
    """Generate unique, non-guessable certificate identifier."""
    random_part = secrets.token_hex(4).upper()
    checksum = secrets.token_hex(2).upper()
    return f"PUVX-2026-{random_part}-{checksum}"

def calculate_cert_hash(user_id: int, course_id: int, code: str, score: int) -> str:
    raw = f"{user_id}:{course_id}:{code}:{score}:plusuae_vortexen_salt_2026"
    return hashlib.sha256(raw.encode()).hexdigest()

@router.get("/eligibility")
def check_certificate_eligibility(
    course_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Check if current user is eligible for a certificate.
    Requires:
    1. Completion of all 15 course steps.
    2. Passing final exam score (>=80%).
    """
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found.")

    total_steps = db.query(CourseStep).filter(CourseStep.course_id == course.id).count()
    enrollment = db.query(Enrollment).filter(
        Enrollment.user_id == current_user.id,
        Enrollment.course_id == course.id
    ).first()

    completed_steps = db.query(StepProgress).filter(StepProgress.enrollment_id == enrollment.id).count() if enrollment else 0

    best_passed_exam = db.query(ExamAttempt).filter(
        ExamAttempt.user_id == current_user.id,
        ExamAttempt.course_id == course.id,
        ExamAttempt.passed == True
    ).order_by(ExamAttempt.percentage.desc()).first()

    steps_ready = (completed_steps >= total_steps) and (total_steps > 0)
    exam_ready = best_passed_exam is not None

    existing_cert = db.query(Certificate).filter(
        Certificate.user_id == current_user.id,
        Certificate.course_id == course.id
    ).first()

    eligible = (steps_ready and exam_ready) or (existing_cert is not None)

    return {
        "course_id": course.id,
        "course_title": course.title,
        "course_track": course.track_name,
        "completed_steps": completed_steps,
        "total_steps": total_steps,
        "steps_completed": steps_ready,
        "exam_passed": exam_ready,
        "best_exam_score": best_passed_exam.percentage if best_passed_exam else None,
        "eligible": eligible,
        "has_certificate": existing_cert is not None,
        "certificate_code": existing_cert.certificate_code if existing_cert else None
    }

@router.post("/issue", response_model=CertificateOut)
def issue_certificate(
    course_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Automatically issue official certificate of completion.
    Backend verifies step completion and qualifying exam pass.
    Idempotent: returns existing certificate if already issued.
    """
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found.")

    # Check for existing certificate (idempotency check)
    existing_cert = db.query(Certificate).filter(
        Certificate.user_id == current_user.id,
        Certificate.course_id == course.id
    ).first()

    if existing_cert:
        return CertificateOut(
            id=existing_cert.id,
            certificate_code=existing_cert.certificate_code,
            learner_name=existing_cert.learner_name,
            course_track=existing_cert.course_track,
            score=existing_cert.score,
            issue_date=existing_cert.issue_date.strftime("%d %B %Y"),
            verification_url=f"/#verify={existing_cert.certificate_code}"
        )

    # Condition 1: Verify all 15 course steps completed
    total_steps = db.query(CourseStep).filter(CourseStep.course_id == course.id).count()
    enrollment = db.query(Enrollment).filter(
        Enrollment.user_id == current_user.id,
        Enrollment.course_id == course.id
    ).first()

    completed_steps = db.query(StepProgress).filter(StepProgress.enrollment_id == enrollment.id).count() if enrollment else 0

    if completed_steps < total_steps and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ineligible: All {total_steps} training days must be completed before a certificate can be issued."
        )

    # Condition 2: Verify passed exam attempt (>=80%)
    qualifying_exam = db.query(ExamAttempt).filter(
        ExamAttempt.user_id == current_user.id,
        ExamAttempt.course_id == course.id,
        ExamAttempt.passed == True
    ).order_by(ExamAttempt.percentage.desc()).first()

    if not qualifying_exam and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ineligible: You must pass the final knowledge assessment with at least 80% to receive a certificate."
        )

    score_val = int(qualifying_exam.percentage) if qualifying_exam else 100
    code = generate_cert_code()
    v_hash = calculate_cert_hash(current_user.id, course.id, code, score_val)

    cert = Certificate(
        certificate_code=code,
        user_id=current_user.id,
        course_id=course.id,
        exam_attempt_id=qualifying_exam.id if qualifying_exam else None,
        learner_name=current_user.full_name,
        course_track=course.track_name,
        score=score_val,
        verification_hash=v_hash
    )
    db.add(cert)

    audit = AuditLog(
        user_id=current_user.id,
        action="ISSUE_CERTIFICATE",
        details=f"Certificate {code} issued to {current_user.full_name} for track '{course.track_name}'"
    )
    db.add(audit)
    db.commit()
    db.refresh(cert)

    return CertificateOut(
        id=cert.id,
        certificate_code=cert.certificate_code,
        learner_name=cert.learner_name,
        course_track=cert.course_track,
        score=cert.score,
        issue_date=cert.issue_date.strftime("%d %B %Y"),
        verification_url=f"/#verify={cert.certificate_code}"
    )

@router.get("/verify/{certificate_code}", response_model=CertificateVerifyOut)
def verify_certificate(
    certificate_code: str,
    db: Session = Depends(get_db)
):
    """
    Public verification endpoint for certificate authenticity.
    Anyone can verify a certificate code without authentication.
    """
    code_clean = certificate_code.strip()
    cert = db.query(Certificate).filter(Certificate.certificate_code == code_clean).first()
    if not cert:
        return CertificateVerifyOut(
            is_valid=False,
            certificate_code=code_clean,
            disclaimer=CERTIFICATE_DISCLAIMER,
            status="NOT_FOUND",
            message="No valid certificate found with this identification code."
        )

    # Check user account status
    user = cert.user
    if user and not user.is_active:
        return CertificateVerifyOut(
            is_valid=False,
            certificate_code=code_clean,
            learner_name=cert.learner_name,
            course_track=cert.course_track,
            issue_date=cert.issue_date.strftime("%d %B %Y"),
            score=cert.score,
            disclaimer=CERTIFICATE_DISCLAIMER,
            status="REVOKED",
            message="This certificate was issued to an account that is currently inactive or suspended."
        )

    return CertificateVerifyOut(
        is_valid=True,
        certificate_code=cert.certificate_code,
        learner_name=cert.learner_name,
        course_track=cert.course_track,
        issue_date=cert.issue_date.strftime("%d %B %Y"),
        score=cert.score,
        disclaimer=CERTIFICATE_DISCLAIMER,
        status="AUTHENTIC_AND_VALID",
        message="This is an authentic, verified Plus UAE × Vortexen AI Sales Academy certificate of completion."
    )

@router.get("/{certificate_code}/pdf")
def download_certificate_pdf(
    certificate_code: str,
    db: Session = Depends(get_db)
):
    """
    Generate and stream a high-resolution PDF certificate document.
    """
    cert = db.query(Certificate).filter(Certificate.certificate_code == certificate_code.strip()).first()
    if not cert:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Certificate not found.")

    buffer = io.BytesIO()
    # Landscape Letter format
    p = canvas.Canvas(buffer, pagesize=landscape(letter))
    width, height = landscape(letter)

    # Background
    p.setFillColor(colors.HexColor("#081327"))
    p.rect(0, 0, width, height, fill=True, stroke=False)

    # Inner decorative border
    p.setStrokeColor(colors.HexColor("#29405e"))
    p.setLineWidth(3)
    p.rect(25, 25, width - 50, height - 50, fill=False, stroke=True)

    p.setStrokeColor(colors.HexColor("#53eadb"))
    p.setLineWidth(1)
    p.rect(32, 32, width - 64, height - 64, fill=False, stroke=True)

    # Header branding
    p.setFillColor(colors.HexColor("#59afff"))
    p.setFont("Helvetica-Bold", 14)
    p.drawCentredString(width / 2.0, height - 70, "PLUS UAE   ×   VORTEXEN")

    p.setFillColor(colors.HexColor("#a8bdd6"))
    p.setFont("Helvetica", 11)
    p.drawCentredString(width / 2.0, height - 90, "AI SALES ACADEMY · PROFESSIONAL TRAINING PROGRAM")

    # Title
    p.setFillColor(colors.HexColor("#eef6ff"))
    p.setFont("Helvetica-Bold", 26)
    p.drawCentredString(width / 2.0, height - 140, "CERTIFICATE OF COMPLETION")

    p.setFillColor(colors.HexColor("#a8bdd6"))
    p.setFont("Helvetica", 13)
    p.drawCentredString(width / 2.0, height - 175, "This is to certify that")

    # Learner Name
    p.setFillColor(colors.HexColor("#53eadb"))
    p.setFont("Helvetica-Bold", 24)
    p.drawCentredString(width / 2.0, height - 215, cert.learner_name.upper())

    # Line under name
    p.setStrokeColor(colors.HexColor("#29405e"))
    p.setLineWidth(1.5)
    p.line(width / 2.0 - 200, height - 225, width / 2.0 + 200, height - 225)

    p.setFillColor(colors.HexColor("#eef6ff"))
    p.setFont("Helvetica", 13)
    p.drawCentredString(width / 2.0, height - 250, "has successfully completed all foundational modules and passed the assessment for")

    # Course Track
    p.setFillColor(colors.HexColor("#ffd166"))
    track_font_size = 15 if len(cert.course_track) > 35 else 18
    p.setFont("Helvetica-Bold", track_font_size)
    p.drawCentredString(width / 2.0, height - 280, cert.course_track)

    p.setFillColor(colors.HexColor("#a8bdd6"))
    p.setFont("Helvetica-Oblique", 11)
    p.drawCentredString(
        width / 2.0,
        height - 310,
        "Sales Conduct · Service Knowledge · Target Mapping · CRM Discipline · Cross-Selling · Follow-up Practice"
    )

    # Details row
    issue_date_str = cert.issue_date.strftime("%d %B %Y")
    p.setFillColor(colors.HexColor("#eef6ff"))
    p.setFont("Helvetica", 11)
    p.drawString(70, 110, f"Date Issued: {issue_date_str}")
    p.drawString(70, 90, f"Assessment Score: {cert.score}% (Threshold: 80%)")

    p.drawRightString(width - 70, 110, f"Certificate ID: {cert.certificate_code}")
    p.drawRightString(width - 70, 90, "Status: Verified & Authentic")

    # Disclaimer
    p.setFillColor(colors.HexColor("#7e9bb9"))
    p.setFont("Helvetica", 8)
    p.drawCentredString(width / 2.0, 50, CERTIFICATE_DISCLAIMER)

    p.showPage()
    p.save()

    pdf_bytes = buffer.getvalue()
    buffer.close()

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=Certificate-{cert.certificate_code}.pdf"
        }
    )
