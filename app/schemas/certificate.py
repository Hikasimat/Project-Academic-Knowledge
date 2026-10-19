from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class CertificateOut(BaseModel):
    id: int
    certificate_code: str
    learner_name: str
    course_track: str
    score: int
    issue_date: str
    verification_url: str

class CertificateVerifyOut(BaseModel):
    is_valid: bool
    certificate_code: str
    learner_name: Optional[str] = None
    course_track: Optional[str] = None
    issue_date: Optional[str] = None
    score: Optional[int] = None
    disclaimer: str
    status: str
    message: str
