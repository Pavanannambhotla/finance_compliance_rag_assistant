from app.vector_store import query_top_k
from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_answer(query: str):
    hits = query_top_k(query, k=5)

    context = "\n\n".join([f"Source {i+1}:\n{doc}" for i, (_, doc, _) in enumerate(hits)])

    prompt = f"""
    You are a compliance assistant. Use the context below to answer the question.

    Context:
    {context}

    Question:
    {query}

    Answer:
    """

    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
    )

    return {
        "answer": completion.choices[0].message.content,
        "sources": hits
    }
