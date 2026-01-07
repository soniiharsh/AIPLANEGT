"""
Human Review Handler (HITL)
---------------------------
Processes human feedback and converts it into
structured learning signals for memory.
"""

class HumanReview:
    def __init__(self, memory):
        self.memory = memory

    def submit_review(
        self,
        input_type: str,
        raw_input: str,
        parsed_problem: dict,
        solution: dict,
        verification: dict,
        user_feedback: str,
        approved: bool
    ):
        """
        Store human feedback as a learning signal.
        """

        record = {
            "input_type": input_type,
            "raw_input": raw_input,
            "parsed_problem": parsed_problem,
            "solution": solution,
            "verification": verification,
            "user_feedback": user_feedback,
            "is_correct": approved
        }

        return self.memory.store(record)
