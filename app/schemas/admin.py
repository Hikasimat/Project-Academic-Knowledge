from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime

class LearnerCreateRequest(BaseModel):
    email: EmailStr
    full_name: str = Field(..., min_length=2, max_length=150)
    course_track: str = Field(..., description="E.g. 'Both companies — Foundation', 'Plus UAE — Sales', 'Vortexen — Technical Sales'")

class LearnerCreateResponse(BaseModel):
    id: int
    email: EmailStr
    full_name: str
    course_track: str
    invitation_token: str
    invitation_url: str
    expires_at: datetime

class LearnerProgressDetail(BaseModel):
    course_id: int
    course_title: str
    course_track: str
    completed_steps: int
    total_steps: int
    progress_percentage: float
    is_completed: bool
    exam_score: Optional[int] = None
    exam_passed: bool = False
    certificate_code: Optional[str] = None
    certificate_issued_at: Optional[datetime] = None

class LearnerListItem(BaseModel):
    id: int
    email: EmailStr
    full_name: str
    role: str
    is_active: bool
    created_at: datetime
    courses: List[LearnerProgressDetail] = []
    invitation_token: Optional[str] = None
    invitation_url: Optional[str] = None

class UserStatusUpdateRequest(BaseModel):
    is_active: bool

class ResetInviteResponse(BaseModel):
    invitation_token: str
    invitation_url: str
    expires_at: datetime
