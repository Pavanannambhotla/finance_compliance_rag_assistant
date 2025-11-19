from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from .models import RAGQuery, RAGAnswer
from .db import SessionLocal, init_db, QueryLog
from .rag_graph import run_rag_pipeline

app = FastAPI(
    title="Finance & Compliance RAG Assistant",
    description="RAG API for answering questions over finance and compliance policies.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.on_event("startup")
def on_startup():
    init_db()


@app.post("/rag/query", response_model=RAGAnswer)
def rag_query(payload: RAGQuery, db: Session = Depends(get_db)):
    answer, sources, latency_ms, top_ids = run_rag_pipeline(payload.question)

    log = QueryLog(
        question=payload.question,
        answer=answer,
        latency_ms=latency_ms,
        top_doc_ids=",".join(top_ids),
    )
    db.add(log)
    db.commit()

    return RAGAnswer(answer=answer, sources=sources, latency_ms=latency_ms)


@app.get("/health")
def health():
    return {"status": "ok"}
