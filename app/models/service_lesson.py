from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.database import Base

def utcnow():
    return datetime.now(timezone.utc)

class ServiceLesson(Base):
    __tablename__ = "service_lessons"

    id = Column(Integer, primary_key=True, index=True)
    company = Column(String(50), nullable=False)  # "plus" or "vortexen"
    name = Column(String(255), nullable=False)
    buyer = Column(String(255), nullable=False)
    dm = Column(String(255), nullable=False)
    process = Column(Text, nullable=False)
    question = Column(String(255), nullable=False)
    risk = Column(String(255), nullable=False)
    is_published = Column(Boolean, default=False, nullable=False)
    created_by_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)

    created_by = relationship("User")
