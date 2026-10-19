from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime

class ServiceLessonCreate(BaseModel):
    company: str = Field(..., pattern="^(plus|vortexen)$")
    name: str = Field(..., min_length=2, max_length=255)
    buyer: str = Field(..., min_length=2, max_length=255)
    dm: str = Field(..., min_length=2, max_length=255)
    process: str = Field(..., min_length=5)
    question: str = Field(..., min_length=5, max_length=255)
    risk: str = Field(..., min_length=5, max_length=255)

class ServiceLessonOut(BaseModel):
    id: int
    company: str
    name: str
    buyer: str
    dm: str
    process: str
    question: str
    risk: str
    is_published: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
