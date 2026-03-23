"""
Schemas Module

Defines request and response models for the Interview API.
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any


# ---------------------------
# Requests
# ---------------------------

class StartInterviewRequest(BaseModel):
    topic: str = Field(..., example="AI in the workplace")
    num_questions: int = Field(default=3, ge=1, le=5)


class AnswerRequest(BaseModel):
    interview_id: str
    question: str
    answer: str


# ---------------------------
# Responses
# ---------------------------

class StartInterviewResponse(BaseModel):
    interview_id: str
    question: str


class AnswerResponse(BaseModel):
    next_question: Optional[str] = None
    completed: bool = False
    summary: Optional[Dict[str, Any]] = None
    analysis: Optional[Dict[str, Any]] = None


class InterviewResponse(BaseModel):
    id: str
    metadata: Dict[str, Any]
    qa_pairs: list
    transcript: str
    summary: Optional[Dict[str, Any]]
    analysis: Optional[Dict[str, Any]]