"""
Interview Routes

Defines API endpoints for the AI Interviewer.
"""

from fastapi import APIRouter, HTTPException

from services.llm_service import LLMClient
from services.storage_service import InterviewStorage
from services.analysis_service import InterviewAnalysis

from models.schemas import (
    StartInterviewRequest,
    StartInterviewResponse,
    AnswerRequest,
    AnswerResponse,
    InterviewResponse
)

router = APIRouter(prefix="/interview", tags=["Interview"])

# Initialize services (simple singleton-style)
llm = LLMClient()
storage = InterviewStorage()
analysis = InterviewAnalysis()


# ---------------------------
# Start Interview
# ---------------------------

@router.post("/start", response_model=StartInterviewResponse)
def start_interview(request: StartInterviewRequest):
    """Start a new interview session."""
    interview = storage.create_interview(
        topic=request.topic,
        total_questions=request.num_questions
    )

    # Generate first question
    question = llm.generate_question(
        topic=request.topic,
        question_number=1,
        total_questions=request.num_questions,
        transcript=""
    )

    return StartInterviewResponse(
        interview_id=interview["id"],
        question=question
    )


# ---------------------------
# Submit Answer
# ---------------------------

@router.post("/answer", response_model=AnswerResponse)
def submit_answer(request: AnswerRequest):
    """Submit an answer and get next question or results."""
    interview = storage.get_interview(request.interview_id)

    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")

    # Save Q&A
    updated = storage.append_qa_pair(
        interview_id=request.interview_id,
        question=request.question,
        answer=request.answer
    )

    q_num = updated["metadata"]["questions_asked"]
    total = updated["metadata"]["total_questions"]

    # ---------------------------
    # Continue Interview
    # ---------------------------
    if q_num < total:
        next_question = llm.generate_question(
            topic=updated["metadata"]["topic"],
            question_number=q_num + 1,
            total_questions=total,
            transcript=updated["transcript"]
        )

        return AnswerResponse(
            next_question=next_question,
            completed=False
        )

    # ---------------------------
    # Finalize Interview
    # ---------------------------
    summary = llm.generate_summary(
        topic=updated["metadata"]["topic"],
        question_count=q_num,
        transcript=updated["transcript"]
    )

    analysis_result = analysis.analyze_transcript(updated)

    final = storage.finalize_interview(
        interview_id=request.interview_id,
        summary=summary,
        analysis=analysis_result
    )

    return AnswerResponse(
        completed=True,
        summary=final["summary"],
        analysis=final["analysis"]
    )


# ---------------------------
# Get Interview by ID
# ---------------------------

@router.get("/{interview_id}", response_model=InterviewResponse)
def get_interview(interview_id: str):
    """Retrieve full interview data."""
    interview = storage.get_interview(interview_id)

    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")

    return interview