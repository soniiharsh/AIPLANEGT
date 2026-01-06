import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # ----------------------------
    # API Keys
    # ----------------------------
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")

    # ----------------------------
    # Model Settings
    # ----------------------------
    LLM_MODEL = "llama3-70b-8192"
    TEMPERATURE = 0.2
    MAX_TOKENS = 4000

    # ----------------------------
    # RAG Settings
    # ----------------------------
    EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
    CHUNK_SIZE = 500
    CHUNK_OVERLAP = 50
    TOP_K_RETRIEVAL = 3

    # ----------------------------
    # Confidence Thresholds
    # ----------------------------
    OCR_CONFIDENCE_THRESHOLD = 0.7
    VERIFIER_CONFIDENCE_THRESHOLD = 0.8

    # ----------------------------
    # Paths
    # ----------------------------
    KNOWLEDGE_BASE_PATH = "./knowledge_base"
    VECTOR_STORE_PATH = "./vector_store"
    MEMORY_DB_PATH = "./memory/solutions.db"
