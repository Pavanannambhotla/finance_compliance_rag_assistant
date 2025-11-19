import os
import uuid
from pathlib import Path
from typing import List

from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.vector_store import add_documents

DATA_DIR = Path("data/source_docs")


def load_all_docs() -> List[str]:
    docs = []
    paths = list(DATA_DIR.glob("**/*"))
    for p in paths:
        if p.suffix.lower() == ".pdf":
            loader = PyPDFLoader(str(p))
            docs.extend(loader.load())
        elif p.suffix.lower() in [".txt", ".md"]:
            loader = TextLoader(str(p), encoding="utf-8")
            docs.extend(loader.load())
    return docs


def main():
    if not DATA_DIR.exists():
        print(f"[ingest_docs] {DATA_DIR} does not exist. Create it and add docs.")
        return

    print("[ingest_docs] Loading documents...")
    docs = load_all_docs()
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=150,
    )
    chunks = splitter.split_documents(docs)

    ids = []
    texts = []
    metas = []

    for ch in chunks:
        ids.append(str(uuid.uuid4()))
        texts.append(ch.page_content)

        page = ch.metadata.get("page")
        if page is None:
            page = -1  # Chroma does NOT allow None

        metas.append({
            "source": ch.metadata.get("source", "unknown"),
            "page": page,
        })

    print(f"[ingest_docs] Ingesting {len(chunks)} chunks into vector store...")
    add_documents(ids, texts, metas)
    print("[ingest_docs] Done.")


if __name__ == "__main__":
    main()
