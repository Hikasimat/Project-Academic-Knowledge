from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class QuestionOut(BaseModel):
    id: int
    question: str
    options: List[str]

class ExamAnswerSubmission(BaseModel):
    question_id: int
    selected_option: int

class ExamSubmitRequest(BaseModel):
    course_id: int
    answers: List[ExamAnswerSubmission]

class ExamResultOut(BaseModel):
    score: int
    total_questions: int
    percentage: float
    passed: bool
    attempt_number: int
    certificate_eligible: bool
    message: str

class ExamAttemptOut(BaseModel):
    id: int
    course_id: int
    attempt_number: int
    score: int
    total_questions: int
    percentage: float
    passed: bool
    created_at: datetime
