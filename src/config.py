import os
from dotenv import load_dotenv

load_dotenv()
# Force offline mode — use cached models only
os.environ["TRANSFORMERS_OFFLINE"] = os.getenv("TRANSFORMERS_OFFLINE", "1")
os.environ["HF_DATASETS_OFFLINE"] = os.getenv("HF_DATASETS_OFFLINE", "1")

# ─── API Keys ────────────────────────────────────────
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# ─── LLM Settings ────────────────────────────────────
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
MAX_TOKENS = int(os.getenv("MAX_TOKENS", "1024"))
TEMPERATURE = float(os.getenv("TEMPERATURE", "0.0"))

# ─── Embedding Settings ──────────────────────────────
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
EMBEDDING_BATCH_SIZE = int(os.getenv("EMBEDDING_BATCH_SIZE", "50"))

# ─── Chunking Settings ───────────────────────────────
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "900"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "150"))

# ─── ChromaDB Settings ───────────────────────────────
CHROMA_DB_PATH = os.getenv("CHROMA_DB_PATH", "chroma_db")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "pdf_chunks")

# ─── Retrieval Settings ──────────────────────────────
TOP_K_RESULTS = int(os.getenv("TOP_K_RESULTS", "5"))
SIMILARITY_THRESHOLD = float(os.getenv("SIMILARITY_THRESHOLD", "0.75"))

# ─── File Settings ───────────────────────────────────
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads")


def validate_groq_key():
    """Call this only in llm_agent.py"""
    if not GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY not found in .env file!")