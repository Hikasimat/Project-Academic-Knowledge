from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, UniqueConstraint
from sqlalchemy.orm import relationship
from app.database import Base

def utcnow():
    return datetime.now(timezone.utc)

class Certificate(Base):
    __tablename__ = "certificates"

    id = Column(Integer, primary_key=True, index=True)
    certificate_code = Column(String(64), unique=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id", ondelete="CASCADE"), nullable=False)
    exam_attempt_id = Column(Integer, ForeignKey("exam_attempts.id", ondelete="SET NULL"), nullable=True)
    learner_name = Column(String(255), nullable=False)
    course_track = Column(String(255), nullable=False)
    score = Column(Integer, nullable=False)
    issue_date = Column(DateTime(timezone=True), default=utcnow, nullable=False)
    verification_hash = Column(String(128), nullable=False)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)

    __table_args__ = (
        UniqueConstraint("user_id", "course_id", name="uq_user_course_certificate"),
    )

    user = relationship("User", back_populates="certificates")
    course = relationship("Course", back_populates="certificates")
    exam_attempt = relationship("ExamAttempt", back_populates="certificate")
