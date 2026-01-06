from anthropic import Anthropic
import json

class ParserAgent:
    def __init__(self, api_key, model):
        self.client = Anthropic(api_key=api_key)
        self.model = model
    
    def parse(self, raw_text):
        """Convert raw input to structured problem"""
        prompt = f"""Parse this math problem into a structured format:

Problem: {raw_text}

Output as JSON with:
- problem_text: cleaned problem statement
- topic: algebra/probability/calculus/linear_algebra
- variables: list of variables
- constraints: list of constraints
- needs_clarification: boolean
- clarification_reason: string if needs_clarification is true

Be thorough in extracting all information."""

        response = self.client.messages.create(
            model=self.model,
            max_tokens=1000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        try:
            parsed = json.loads(response.content[0].text)
            return parsed
        except:
            # Fallback if JSON parsing fails
            return {
                "problem_text": raw_text,
                "topic": "unknown",
                "variables": [],
                "constraints": [],
                "needs_clarification": True,
                "clarification_reason": "Failed to parse problem structure"
            }