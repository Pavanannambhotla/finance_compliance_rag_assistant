import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DB_URL = os.getenv("DB_URL", "sqlite:///./rag_logs.db")  # fallback if no Postgres yet
CHROMA_DIR = os.getenv("CHROMA_DIR", "./chroma_db")

if OPENAI_API_KEY is None:
    raise RuntimeError("OPENAI_API_KEY not set in environment")
