"""
Storage Service Module

Handles persistence of interview data using one file per interview.
Designed for web apps (FastAPI).
"""

import json
import uuid
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime


class InterviewStorage:
    """Manages interview data persistence."""

    def __init__(self, base_dir: str = "data"):
        """
        Initialize storage manager.

        Args:
            base_dir: Base directory for storing interviews
        """
        self.base_path = Path(base_dir)
        self.interviews_path = self.base_path / "interviews"
        self.transcripts_path = self.base_path / "transcripts"

        self.interviews_path.mkdir(parents=True, exist_ok=True)
        self.transcripts_path.mkdir(parents=True, exist_ok=True)

    # ---------------------------
    # Core CRUD Operations
    # ---------------------------

    def create_interview(self, topic: str, total_questions: int) -> Dict[str, Any]:
        """Create a new interview session."""
        interview_id = str(uuid.uuid4())

        interview_data = {
            "id": interview_id,
            "metadata": {
                "created_at": datetime.now().isoformat(),
                "completed_at": None,
                "topic": topic,
                "total_questions": total_questions,
                "questions_asked": 0,
                "status": "in_progress"
            },
            "qa_pairs": [],
            "transcript": "",
            "summary": None,
            "analysis": None
        }

        self._save(interview_id, interview_data)
        return interview_data

    def get_interview(self, interview_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve interview by ID."""
        filepath = self.interviews_path / f"{interview_id}.json"

        if not filepath.exists():
            return None

        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)

    def update_interview(self, interview_id: str, data: Dict[str, Any]) -> None:
        """Save updated interview data."""
        self._save(interview_id, data)

    # ---------------------------
    # Interview Flow Helpers
    # ---------------------------

    def append_qa_pair(
        self,
        interview_id: str,
        question: str,
        answer: str
    ) -> Dict[str, Any]:
        """Add a Q&A pair to an existing interview."""
        interview_data = self.get_interview(interview_id)

        if not interview_data:
            raise ValueError("Interview not found")

        q_num = interview_data["metadata"]["questions_asked"] + 1

        pair = {
            "number": q_num,
            "timestamp": datetime.now().isoformat(),
            "question": question,
            "answer": answer
        }

        interview_data["qa_pairs"].append(pair)
        interview_data["metadata"]["questions_asked"] = q_num

        # Update transcript
        interview_data["transcript"] += (
            f"Q{q_num}: {question}\n\n"
            f"A{q_num}: {answer}\n\n"
        )

        self._save(interview_id, interview_data)
        return interview_data

    def finalize_interview(
        self,
        interview_id: str,
        summary: Dict[str, Any],
        analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Mark interview as completed and attach results."""
        interview_data = self.get_interview(interview_id)

        if not interview_data:
            raise ValueError("Interview not found")

        interview_data["metadata"]["status"] = "completed"
        interview_data["metadata"]["completed_at"] = datetime.now().isoformat()
        interview_data["summary"] = summary
        interview_data["analysis"] = analysis

        self._save(interview_id, interview_data)
        self._save_transcript(interview_data)

        return interview_data

    # ---------------------------
    # Internal Helpers
    # ---------------------------

    def _save(self, interview_id: str, data: Dict[str, Any]) -> None:
        """Write interview data to disk."""
        filepath = self.interviews_path / f"{interview_id}.json"

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def _save_transcript(self, interview_data: Dict[str, Any]) -> None:
        """Save human-readable transcript."""
        topic = interview_data["metadata"]["topic"].replace(" ", "_")[:30]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        filename = f"{topic}_{timestamp}.txt"
        filepath = self.transcripts_path / filename

        content = f"""
INTERVIEW TRANSCRIPT
====================
Topic: {interview_data['metadata']['topic']}
Date: {interview_data['metadata']['created_at']}
Questions: {interview_data['metadata']['questions_asked']}

FULL TRANSCRIPT
---------------
{interview_data['transcript']}

SUMMARY
-------
{json.dumps(interview_data['summary'], indent=2)}

ANALYSIS
--------
{json.dumps(interview_data['analysis'], indent=2)}
"""

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

    # ---------------------------
    # Utility
    # ---------------------------

    @staticmethod
    def build_transcript(qa_pairs: list) -> str:
        """Rebuild transcript from Q&A pairs."""
        transcript = ""
        for pair in qa_pairs:
            transcript += f"Q{pair['number']}: {pair['question']}\n"
            transcript += f"A{pair['number']}: {pair['answer']}\n\n"
        return transcript