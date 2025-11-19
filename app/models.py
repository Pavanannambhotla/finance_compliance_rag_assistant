from pydantic import BaseModel
from typing import List, Optional


class RAGQuery(BaseModel):
    question: str


class RAGAnswer(BaseModel):
    answer: str
    sources: List[str]
    latency_ms: Optional[float] = None
