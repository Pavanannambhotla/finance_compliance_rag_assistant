import time
from typing import List, Tuple
from openai import OpenAI
from .config import OPENAI_API_KEY
from .vector_store import query_top_k

client = OpenAI(api_key=OPENAI_API_KEY)


def build_context(docs: List[Tuple[str, str, dict]]) -> str:
    parts = []
    for idx, (doc_id, text, meta) in enumerate(docs, start=1):
        src = meta.get("source", f"doc_{doc_id}")
        parts.append(f"[Source {idx} - {src}]\n{text}")
    return "\n\n".join(parts)


def generate_answer(question: str, docs: List[Tuple[str, str, dict]]) -> Tuple[str, List[str], float]:
    start = time.time()
    context = build_context(docs)

    system_msg = (
        "You are a helpful assistant answering questions about finance and compliance policies. "
        "Only answer using the given context. If the answer is not in the context, say you don't know."
    )

    messages = [
        {"role": "system", "content": system_msg},
        {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {question}"}
    ]

    resp = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=messages,
            temperature=0.2,
    )

    answer = resp.choices[0].message.content
    latency_ms = (time.time() - start) * 1000

    sources = [m.get("source", doc_id) for doc_id, _, m in docs]
    return answer, sources, latency_ms


def run_rag_pipeline(question: str, k: int = 5):
    """
    Simple RAG graph:
    1) retrieve top-k documents
    2) generate answer from LLM using context
    """
    docs = query_top_k(question, k=k)
    answer, sources, latency_ms = generate_answer(question, docs)
    top_ids = [doc_id for doc_id, _, _ in docs]
    return answer, sources, latency_ms, top_ids
