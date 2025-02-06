import json
import numpy as np
import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from dotenv import load_dotenv

load_dotenv()

# Lire les variables d'environnement
DOCUMENTS_FILE = os.getenv("DOCUMENTS_FILE")
LLM_MODEL_NAME = os.getenv("LLM_MODEL_NAME")

app = FastAPI()

model = SentenceTransformer(LLM_MODEL_NAME)

def load_documents():
    try:
        with open(DOCUMENTS_FILE, "r") as file:
            documents = json.load(file)
            return {doc["id"]: doc for doc in documents}
    except FileNotFoundError:
        return {}

documents_db = load_documents()

class Query(BaseModel):
    query_text: str

@app.post("/retrieve_documents")
def retrieve_documents(query: Query):
    retrieve_documents = model.encode(query.query_text).reshape(1, -1)

    if not documents_db:
        raise HTTPException(status_code=404, detail="No documents available")

    document_embeddings = np.array([doc["embedding"] for doc in documents_db.values()])

    similarities = cosine_similarity(retrieve_documents, document_embeddings)

    sorted_indices = np.argsort(similarities[0])[::-1]

    top_5_documents = []
    for idx in sorted_indices[:5]:
        doc = documents_db[list(documents_db.keys())[idx]]
        top_5_documents.append({
            "id": doc["id"],
            "content": doc["content"]
        })

    return top_5_documents
