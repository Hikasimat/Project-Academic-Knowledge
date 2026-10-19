from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, UniqueConstraint
from sqlalchemy.orm import relationship
from app.database import Base

def utcnow():
    return datetime.now(timezone.utc)

class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(100), unique=True, index=True, nullable=False)
    title = Column(String(255), nullable=False)
    track_name = Column(String(255), unique=True, nullable=False)  # "Both companies — Foundation", "Plus UAE — Sales", "Vortexen — Technical Sales"
    description = Column(Text, nullable=False)

    steps = relationship("CourseStep", back_populates="course", cascade="all, delete-orphan", order_by="CourseStep.step_number")
    enrollments = relationship("Enrollment", back_populates="course", cascade="all, delete-orphan")
    exam_attempts = relationship("ExamAttempt", back_populates="course", cascade="all, delete-orphan")
    certificates = relationship("Certificate", back_populates="course", cascade="all, delete-orphan")

class CourseStep(Base):
    __tablename__ = "course_steps"

    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id", ondelete="CASCADE"), nullable=False)
    step_number = Column(Integer, nullable=False)
    day_number = Column(Integer, nullable=False)
    section_number = Column(Integer, default=1, nullable=True)
    section_title = Column(String(255), nullable=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    target_section = Column(String(100), nullable=False, default="training")  # UI section ID to navigate to
    is_mandatory = Column(Boolean, default=True, nullable=False)

    __table_args__ = (
        UniqueConstraint("course_id", "step_number", name="uq_course_step_number"),
    )

    course = relationship("Course", back_populates="steps")
    progress_records = relationship("StepProgress", back_populates="step", cascade="all, delete-orphan")

class Enrollment(Base):
    __tablename__ = "enrollments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id", ondelete="CASCADE"), nullable=False)
    is_completed = Column(Boolean, default=False, nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)

    __table_args__ = (
        UniqueConstraint("user_id", "course_id", name="uq_user_course_enrollment"),
    )

    user = relationship("User", back_populates="enrollments")
    course = relationship("Course", back_populates="enrollments")
    step_progress = relationship("StepProgress", back_populates="enrollment", cascade="all, delete-orphan")

class StepProgress(Base):
    __tablename__ = "step_progress"

    id = Column(Integer, primary_key=True, index=True)
    enrollment_id = Column(Integer, ForeignKey("enrollments.id", ondelete="CASCADE"), nullable=False)
    step_id = Column(Integer, ForeignKey("course_steps.id", ondelete="CASCADE"), nullable=False)
    completed_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)

    __table_args__ = (
        UniqueConstraint("enrollment_id", "step_id", name="uq_enrollment_step_progress"),
    )

    enrollment = relationship("Enrollment", back_populates="step_progress")
    step = relationship("CourseStep", back_populates="progress_records")
