"""
Explainer Agent
---------------
Converts a verified solution into a clear, step-by-step explanation
suitable for JEE-level students.
"""

from anthropic import Anthropic
import json


class ExplainerAgent:
    def __init__(self, api_key: str, model: str):
        self.client = Anthropic(api_key=api_key)
        self.model = model

    def explain(self, problem: dict, solution: dict, verification: dict):
        """
        Generate a student-friendly explanation.

        Parameters:
        - problem: structured problem from ParserAgent
        - solution: raw solution from SolverAgent
        - verification: result from VerifierAgent
        """

        # Safety check: explain only verified solutions
        if not verification.get("is_correct", False):
            return {
                "explanation": (
                    "The solution could not be confidently verified. "
                    "Please review the problem or provide clarification."
                )
            }

        prompt = f"""
You are a math tutor preparing a JEE-style explanation.

Problem:
{problem['problem_text']}

Verified Final Answer:
{solution['solution']}

Guidelines:
- Explain step-by-step in simple language
- Justify each mathematical step
- Highlight formulas used
- Mention common mistakes briefly if relevant
- Do NOT introduce new calculations
- Do NOT change the final answer
- Keep explanation concise and exam-oriented

Write the explanation clearly.
"""

        response = self.client.messages.create(
            model=self.model,
            max_tokens=1200,
            messages=[{"role": "user", "content": prompt}]
        )

        return {
            "explanation": response.content[0].text.strip()
        }
