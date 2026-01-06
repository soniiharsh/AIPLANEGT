class VerifierAgent:
    def __init__(self, client, model, threshold=0.8):
        self.client = client
        self.model = model
        self.threshold = threshold
    
    def verify(self, problem, solution):
        """Check solution correctness"""
        prompt = f"""Verify this solution carefully:

Problem: {problem['problem_text']}
Solution: {solution['solution']}

Check for:
1. Mathematical correctness
2. Unit consistency
3. Domain validity (e.g., probabilities between 0 and 1)
4. Edge cases
5. Common mistakes

Output JSON:
{{
  "is_correct": boolean,
  "confidence": float (0-1),
  "issues": [list of issues if any],
  "needs_human_review": boolean
}}"""

        response = self.client.messages.create(
            model=self.model,
            max_tokens=1000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        try:
            result = json.loads(response.content[0].text)
            result["needs_human_review"] = (
                not result["is_correct"] or 
                result["confidence"] < self.threshold
            )
            return result
        except:
            return {
                "is_correct": False,
                "confidence": 0.0,
                "issues": ["Verification failed"],
                "needs_human_review": True
            }