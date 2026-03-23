Analyze the interview transcript and generate a structured summary.

Topic: {topic}  
Number of questions: {question_count}

Transcript:
{transcript}

Return a valid JSON object with this structure:

{{
  "topic": "string",
  "question_count": number,
  "key_themes": ["theme1", "theme2"],
  "summary": "2-3 paragraph summary of key ideas and patterns",
  "insights": ["insight1", "insight2"],
  "follow_up_questions": ["question1", "question2"],
  "sentiment_indicators": ["descriptor1"],
  "notable_quotes": ["short quote"]
}}

Rules:
- Output ONLY valid JSON
- No markdown, no explanations
- Keep items concise and non-repetitive