# ✅ USE everywhere
from google import genai

import json


class ParserAgent:
    def __init__(self, api_key, model="models/gemini-1.0-pro"
):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model)

        # Hard verification (fail fast)
        try:
            self.model.generate_content("Reply with OK only.")
        except Exception as e:
            raise RuntimeError(f"Gemini API key verification failed: {e}")

    def parse(self, raw_text):
        """Convert raw math input into structured JSON"""

        prompt = f"""
Parse the following math problem and return ONLY valid JSON.
Do NOT include explanations, markdown, or extra text.

Problem:
{raw_text}

JSON schema:
{{
  "problem_text": "string",
  "topic": "algebra | probability | calculus | linear_algebra",
  "variables": ["string"],
  "constraints": ["string"],
  "needs_clarification": boolean,
  "clarification_reason": "string"
}}

Return ONLY the JSON object.
"""

        try:
            response = self.model.generate_content(
                prompt,
                generation_config={
                    "temperature": 0.0,
                    "max_output_tokens": 1000
                }
            )

            # Gemini-safe text extraction
            raw_output = response.text.strip()

            # Defensive cleanup (Gemini may still fence JSON)
            if "```" in raw_output:
                raw_output = raw_output.split("```")[1].strip()

            return json.loads(raw_output)

        except Exception:
            # Fallback (never crash pipeline)
            return {
                "problem_text": raw_text,
                "topic": "unknown",
                "variables": [],
                "constraints": [],
                "needs_clarification": True,
                "clarification_reason": "Failed to parse structured output"
            }
