# Finance & Compliance RAG Assistant

This project implements a **Retrieval-Augmented Generation (RAG) API** for
finance and compliance workflows.

It lets analysts and case owners ask natural language questions over internal
policies, procedures, and regulatory documents. The system retrieves relevant
snippets and passes them to an LLM to generate grounded answers.

---

## ✨ Features

- RAG pipeline over finance/compliance documents
- Vector search with custom scoring
- LLM-based answer generation (Azure OpenAI or OpenAI)
- FastAPI HTTP API for integration with other tools
- Query & response logging in PostgreSQL
- Simple LangGraph-style flow to separate retrieval and generation steps

---

## 🧱 Tech Stack

- **Backend:** Python, FastAPI
- **LLM:** Azure OpenAI / OpenAI API
- **RAG / Orchestration:** LangGraph-style graph in `rag_graph.py`
- **Vector Store:** Local ChromaDB (can be swapped for pgvector)
- **Database:** PostgreSQL (logging queries/responses)
- **Other:** SQLAlchemy, Pydantic, Uvicorn

---

## 📂 Project Layout

```text
app/
  main.py          # FastAPI app and endpoints
  config.py        # Env-based configuration
  rag_graph.py     # RAG pipeline / LangGraph-style flow
  vector_store.py  # Vector index wrapper
  db.py            # PostgreSQL connection + models
  models.py        # Pydantic schemas

scripts/
  ingest_docs.py   # CLI script to ingest finance/compliance docs into vector DB
data/source_docs/
  *.pdf, *.txt     # place your policy/procedure docs here
