import os
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pypdf import PdfReader
from app.vector_store import add_documents

def extract_text_from_file(path: str) -> str:
    ext = os.path.splitext(path)[1].lower()

    if ext == ".pdf":
        reader = PdfReader(path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text

    elif ext in [".txt", ".md"]:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()

    else:
        raise ValueError(f"Unsupported file type: {ext}")


def chunk_text(text: str):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=150,
        separators=["\n\n", "\n", ".", " ", ""]
    )
    return splitter.split_text(text)


def process_uploaded_document(path: str):
    # 1. Extract
    raw_text = extract_text_from_file(path)

    # 2. Chunk
    chunks = chunk_text(raw_text)

    # 3. Insert into ChromaDB
    ids = [os.path.basename(path) + f"_{i}" for i in range(len(chunks))]
    metas = [{"source": os.path.basename(path)} for _ in chunks]

    add_documents(ids, chunks, metas)

    return len(chunks)
