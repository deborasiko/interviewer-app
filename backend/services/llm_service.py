"""
LLM Integration Module

Handles all interactions with the Language Model using Azure AI Inference (GitHub Models)
"""

import os
import json
import re
from typing import Optional
from pathlib import Path


class LLMClient:
    """Manages LLM API calls and responses."""
    
    def __init__(self, model: str = "microsoft/Phi-4", temperature: float = 0.7):
        """
        Initialize the LLM client.
        
        Args:
            model: Model name (default: microsoft/Phi-4)
            temperature: Temperature for generation (default: 0.7)
        """
        self.model = model
        self.temperature = temperature
        self.client = self._init_client()
    
    def _init_client(self):
        """Initialize the Azure AI Inference client."""
        try:
            from azure.ai.inference import ChatCompletionsClient
            from azure.core.credentials import AzureKeyCredential
        except ImportError:
            raise ImportError(
                "Azure AI Inference library not installed. Run: pip install azure-ai-inference"
            )
        
        github_token = os.getenv("GITHUB_TOKEN")
        if not github_token:
            raise ValueError(
                "GITHUB_TOKEN environment variable not set. "
                "Generate a PAT token from https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens"
            )
        
        return ChatCompletionsClient(
            endpoint="https://models.github.ai/inference",
            credential=AzureKeyCredential(github_token),
        )
    
    def generate_question(
        self,
        topic: str,
        question_number: int,
        total_questions: int,
        transcript: str
    ) -> str:

        system_template = self._load_prompt("prompts/system.md")
        user_template = self._load_prompt("prompts/questions.md")

        formatted_transcript = transcript if transcript else "No previous questions yet."

        system_prompt = system_template

        user_prompt = user_template.format(
            topic=topic,
            question_number=question_number,
            total_questions=total_questions,
            transcript=formatted_transcript
        )

        return self._call_llm(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            max_tokens=200
        )
    
    def generate_summary(
        self,
        topic: str,
        question_count: int,
        transcript: str
    ) -> dict:

        system_prompt = "You are a precise data analyst. Return only valid JSON."

        prompt_template = self._load_prompt("prompts/summary.md")

        user_prompt = prompt_template.format(
            topic=topic,
            question_count=question_count,
            transcript=transcript
        )

        max_retries = 3

        for attempt in range(max_retries):
            response = self._call_llm(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                max_tokens=1500,
                temperature=0.2  # more deterministic
            )

            try:
                json_match = re.search(r'\{.*\}', response, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group())
            except (json.JSONDecodeError, AttributeError):
                import logging
                logger = logging.getLogger(__name__)

                if attempt < max_retries - 1:
                    logger.warning(f"Invalid JSON (attempt {attempt + 1}/{max_retries})")

                    user_prompt += "\n\nIMPORTANT: Return ONLY valid JSON."

                else:
                    logger.error("Failed to get valid JSON after retries")
                    return self._create_placeholder_summary(topic, question_count)

        return self._create_placeholder_summary(topic, question_count)
    
    def _call_llm(
        self,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int = 500,
        temperature: Optional[float] = None
    ) -> str:
        try:
            from azure.ai.inference.models import SystemMessage, UserMessage

            response = self.client.complete(
                messages=[
                    SystemMessage(content=system_prompt),
                    UserMessage(content=user_prompt)
                ],
                model=self.model,
                temperature=temperature if temperature is not None else self.temperature,
                top_p=0.9,
                presence_penalty=0.4,
                frequency_penalty=0.3,
                max_tokens=max_tokens,
                stop=["\n\n", "Explanation:", "Answer:"],
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error("LLM API Error", exc_info=True)
            raise
    
    def _load_prompt(self, prompt_path: str) -> str:
        """Load prompt template from file."""
        path = Path(prompt_path)
        if path.exists():
            return path.read_text()
        else:
            print(f"  ⚠️ Warning: Prompt file {prompt_path} not found")
            return "{topic}\n{transcript}"
    
    @staticmethod
    def _create_placeholder_summary(topic: str, question_count: int) -> dict:
        """Create a basic summary when LLM fails."""
        return {
            "topic": topic,
            "question_count": question_count,
            "key_themes": ["General discussion"],
            "summary": "Interview completed on the topic. See full transcript for details.",
            "insights": ["Interview was conducted successfully"],
            "follow_up_questions": ["Consider deeper exploration in follow-up"],
            "sentiment_indicators": ["Professional"],
            "notable_quotes": []
        }
