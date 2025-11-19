import os
from typing import List
import chromadb
from chromadb.utils import embedding_functions

from .config import CHROMA_DIR, OPENAI_API_KEY

# Embedding function
openai_ef = embedding_functions.OpenAIEmbeddingFunction(
    api_key=OPENAI_API_KEY,
    model_name="text-embedding-3-small"
)

COLLECTION_NAME = "finance_compliance_docs"


# ----------------------------------------------------------------------
# New Chroma client (PersistentClient)
# ----------------------------------------------------------------------
def get_chroma_client():
    os.makedirs(CHROMA_DIR, exist_ok=True)
    return chromadb.PersistentClient(path=CHROMA_DIR)


# ----------------------------------------------------------------------
# Get or create collection
# ----------------------------------------------------------------------
def get_or_create_collection():
    client = get_chroma_client()

    try:
        return client.get_collection(COLLECTION_NAME)
    except Exception:
        return client.create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},
            embedding_function=openai_ef
        )


# ----------------------------------------------------------------------
# Add docs
# ----------------------------------------------------------------------
def clean_metadata(md: dict) -> dict:
    cleaned = {}
    for key, value in md.items():
        if isinstance(value, dict):
            # Recursively clean nested dictionaries
            cleaned[key] = clean_metadata(value)
        elif value is None:
            cleaned[key] = ""
        else:
            cleaned[key] = value
    return cleaned


def add_documents(ids: List[str], texts: List[str], metadatas: List[dict]):
    metadatas = [clean_metadata(m) for m in metadatas]

    coll = get_or_create_collection()
    coll.add(ids=ids, documents=texts, metadatas=metadatas)

# ----------------------------------------------------------------------
# Query docs
# ----------------------------------------------------------------------
def query_top_k(query: str, k: int = 5):
    coll = get_or_create_collection()
    result = coll.query(
        query_texts=[query],
        n_results=k,
    )

    ids = result["ids"][0]
    docs = result["documents"][0]
    metas = result["metadatas"][0]

    return list(zip(ids, docs, metas))
