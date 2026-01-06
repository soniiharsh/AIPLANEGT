class SolverAgent:
    def __init__(self, client, model, rag_retriever):
        self.client = client
        self.model = model
        self.rag = rag_retriever
    
    def solve(self, structured_problem):
        """Solve using RAG context"""
        # Retrieve relevant knowledge
        context_docs = self.rag.retrieve(
            structured_problem["problem_text"]
        )
        
        context = "\n\n".join([
            f"Source: {doc['source']}\n{doc['content']}"
            for doc in context_docs
        ])
        
        prompt = f"""Given this context from our knowledge base:

{context}

Solve this problem:
{json.dumps(structured_problem, indent=2)}

Provide:
1. Final answer
2. Step-by-step solution
3. Any formulas used

Be precise and show all work."""

        response = self.client.messages.create(
            model=self.model,
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return {
            "solution": response.content[0].text,
            "context_used": context_docs
        }