from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class CourseStepOut(BaseModel):
    id: int
    step_number: int
    day_number: int
    section_number: int = 1
    section_title: Optional[str] = None
    title: str
    description: Optional[str] = None
    target_section: str
    topics: Optional[List[str]] = []
    is_mandatory: bool
    is_completed: bool
    is_unlocked: bool
    completed_at: Optional[datetime] = None

class CourseOut(BaseModel):
    id: int
    code: str
    title: str
    track_name: str
    description: str
    completed_steps: int
    total_steps: int
    progress_percentage: float
    is_completed: bool
    exam_eligible: bool

class CourseDetailOut(CourseOut):
    steps: List[CourseStepOut]

class StepCompleteRequest(BaseModel):
    step_id: int

class StepCompleteResponse(BaseModel):
    success: bool
    message: str
    step_number: int
    completed_steps: int
    total_steps: int
    progress_percentage: float
    next_step_unlocked: Optional[int] = None
    exam_eligible: bool
