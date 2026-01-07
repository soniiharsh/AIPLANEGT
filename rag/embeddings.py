"""
Embeddings Module
-----------------
Handles text embedding for RAG using SentenceTransformers.
"""

from sentence_transformers import SentenceTransformer
import numpy as np


class EmbeddingModel:
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        """
        Initialize embedding model.

        This model is:
        - Lightweight
        - Fast
        - Good enough for math text retrieval
        """
        self.model_name = model_name
        self.model = SentenceTransformer(model_name)

    def embed_text(self, text: str) -> np.ndarray:
        """
        Embed a single text string.
        """
        embedding = self.model.encode(
            text,
            convert_to_numpy=True,
            normalize_embeddings=True
        )
        return embedding

    def embed_documents(self, texts: list[str]) -> np.ndarray:
        """
        Embed multiple documents/chunks.
        """
        embeddings = self.model.encode(
            texts,
            convert_to_numpy=True,
            normalize_embeddings=True
        )
        return embeddings
