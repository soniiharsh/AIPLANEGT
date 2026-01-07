"""
Retriever Module
----------------
Performs similarity search over embedded knowledge chunks
using FAISS.
"""

import faiss
import numpy as np
from rag.embeddings import EmbeddingModel


class Retriever:
    def __init__(self, documents: list[dict], embedding_model: EmbeddingModel):
        """
        Parameters:
        - documents: list of dicts with keys {"content", "source"}
        - embedding_model: instance of EmbeddingModel
        """
        self.documents = documents
        self.embedding_model = embedding_model

        self.index = None
        self.embeddings = None

        self._build_index()

    def _build_index(self):
        """Build FAISS index from document embeddings."""
        texts = [doc["content"] for doc in self.documents]

        # Generate embeddings
        self.embeddings = self.embedding_model.embed_documents(texts)
        dim = self.embeddings.shape[1]

        # FAISS cosine similarity (via inner product on normalized vectors)
        self.index = faiss.IndexFlatIP(dim)
        self.index.add(self.embeddings)

    def retrieve(self, query: str, top_k: int = 3):
        """
        Retrieve top-k most relevant documents for a query.
        """
        query_embedding = self.embedding_model.embed_text(query)
        query_embedding = np.expand_dims(query_embedding, axis=0)

        scores, indices = self.index.search(query_embedding, top_k)

        results = []
        for idx, score in zip(indices[0], scores[0]):
            if idx == -1:
                continue

            doc = self.documents[idx]
            results.append({
                "content": doc["content"],
                "source": doc.get("source", "unknown"),
                "score": float(score)
            })

        return results
