"""
Intent Router Agent
-------------------
Determines the math domain and routes the problem
to the appropriate solving strategy/tools.
"""

from anthropic import Anthropic


class RouterAgent:
    def __init__(self, api_key: str, model: str):
        self.client = Anthropic(api_key=api_key)
        self.model = model

    def route(self, parsed_problem: dict):
        """
        Decide problem category and required tools.

        Returns:
        {
            "topic": str,
            "route": str,
            "tools": list,
            "confidence": float
        }
        """

        # ---------- 1. Fast deterministic routing ----------
        topic = parsed_problem.get("topic", "").lower()
        text = parsed_problem.get("problem_text", "").lower()

        if topic in ["probability"]:
            return self._build_route(
                topic="probability",
                route="probability_solver",
                tools=["rag", "calculator"],
                confidence=0.95
            )

        if topic in ["calculus"]:
            return self._build_route(
                topic="calculus",
                route="calculus_solver",
                tools=["rag", "calculator"],
                confidence=0.95
            )

        if topic in ["algebra", "linear_algebra"]:
            return self._build_route(
                topic=topic,
                route="algebra_solver",
                tools=["rag", "calculator"],
                confidence=0.9
            )

        # ---------- 2. Keyword-based fallback ----------
        if any(k in text for k in ["probability", "coin", "dice", "chance"]):
            return self._build_route(
                topic="probability",
                route="probability_solver",
                tools=["rag", "calculator"],
                confidence=0.8
            )

        if any(k in text for k in ["limit", "derivative", "differentiate", "rate of change"]):
            return self._build_route(
                topic="calculus",
                route="calculus_solver",
                tools=["rag", "calculator"],
                confidence=0.8
            )

        if any(k in text for k in ["matrix", "determinant", "vector"]):
            return self._build_route(
                topic="linear_algebra",
                route="linear_algebra_solver",
                tools=["rag", "calculator"],
                confidence=0.8
            )

        # ---------- 3. LLM-based classification (last resort) ----------
        return self._llm_route(parsed_problem)

    def _llm_route(self, parsed_problem: dict):
        """
        Use LLM only if deterministic routing fails.
        """

        prompt = f"""
Classify the following math problem into ONE category:
- algebra
- probability
- calculus
- linear_algebra

Problem:
{parsed_problem['problem_text']}

Respond with only the category name.
"""

        response = self.client.messages.create(
            model=self.model,
            max_tokens=20,
            messages=[{"role": "user", "content": prompt}]
        )

        topic = response.content[0].text.strip().lower()

        return self._build_route(
            topic=topic,
            route=f"{topic}_solver",
            tools=["rag", "calculator"],
            confidence=0.6
        )

    def _build_route(self, topic, route, tools, confidence):
        return {
            "topic": topic,
            "route": route,
            "tools": tools,
            "confidence": confidence
        }
