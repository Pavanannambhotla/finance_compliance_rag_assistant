from fastapi import FastAPI, UploadFile, File
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from chromadb import Client
import os

from app.ingestion import process_uploaded_document
from app.rag import generate_answer

app = FastAPI(title="Finance Compliance RAG API")

# ---- CORS for frontend JS ----
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---- Serve the frontend folder ----
# This makes all /frontend/... files accessible
app.mount("/frontend", StaticFiles(directory="frontend"), name="frontend")

# ---- Serve index.html at root "/" ----
@app.get("/")
def serve_frontend():
    return FileResponse("frontend/index.html")


# ---- RAG Ask Endpoint ----
class QueryRequest(BaseModel):
    question: str

@app.post("/ask")
async def ask_rag(req: QueryRequest):
    result = generate_answer(req.question)
    return result


# ---- Document Upload Endpoint ----
@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    # Ensure folder exists
    os.makedirs("data/uploads", exist_ok=True)

    # 1. Save file locally
    contents = await file.read()
    save_path = os.path.join("data/uploads", file.filename)

    with open(save_path, "wb") as f:
        f.write(contents)

    # 2. Process file into vector DB
    chunks_added = process_uploaded_document(save_path)

    return {
        "status": "success",
        "filename": file.filename,
        "chunks_inserted": chunks_added
    }
@app.get("/db/documents")
def list_documents():
    try:
        client = Client()
        
        try:
            coll = client.get_collection("finance_rag")
        except:
            coll = client.create_collection("finance_rag")

        data = coll.get()

        by_doc = {}
        for meta in data.get("metadatas", []):
            doc = meta.get("document")
            if doc:
                by_doc.setdefault(doc, 0)
                by_doc[doc] += 1

        return [{"document": k, "chunks": v} for k, v in by_doc.items()]

    except Exception as e:
        print("Error listing documents:", e)
        raise HTTPException(status_code=500, detail=str(e))
@app.get("/db/document/{doc_name}")
def get_document_chunks(doc_name: str):
    client = Client()
    coll = client.get_collection("finance_rag")

    results = coll.get(where={"source": doc_name})

    return {
        "document": doc_name,
        "count": len(results["ids"]),
        "chunks": [
            {
                "id": results["ids"][i],
                "text": results["documents"][i],
                "metadata": results["metadatas"][i],
            }
            for i in range(len(results["ids"]))
        ]
    }
