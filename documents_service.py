import json
import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
import uuid
from typing import List
from dotenv import load_dotenv

# Charger les variables d'environnement à partir du fichier .env
load_dotenv()

# Lire les variables d'environnement
DOCUMENTS_FILE = os.getenv("DOCUMENTS_FILE")
LLM_MODEL_NAME = os.getenv("LLM_MODEL_NAME")

app = FastAPI()

# Charger le modèle d'embedding
embedding_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

# Définir le chemin du fichier de stockage des documents
DOCUMENTS_FILE = "documents.json"

# Document model
class Document(BaseModel):
    id: str
    content: str
    embedding: List[float]

# Response model for document retrieval (without embedding)
class DocumentResponse(BaseModel):
    id: str
    content: str

# Response model for document retrieval (without embedding)
class DocumentResponseEm(BaseModel):
    id: str
    content: str
    embedding: List[float]

# Request model for adding documents
class DocumentCreate(BaseModel):
    content: str

def load_documents():
    try:
        with open(DOCUMENTS_FILE, "r") as file:
            documents = json.load(file)
            return {doc["id"]: Document(**doc) for doc in documents}
    except FileNotFoundError:
        return {}

def save_documents(documents):
    with open(DOCUMENTS_FILE, "w") as file:
        json.dump([doc.dict() for doc in documents.values()], file)

documents_db = load_documents()

@app.post("/documents", response_model=Document)
def add_document(doc: DocumentCreate):
    """Ajouter un nouveau document."""
    # Générer l'embeddding pour le contenu du document
    embedding = embedding_model.encode(doc.content).tolist()
    
    # Créer un ID unique et stocker le document
    doc_id = str(uuid.uuid4())
    document = Document(id=doc_id, content=doc.content, embedding=embedding)
    documents_db[doc_id] = document
    
    # Sauvegarder les documents dans le fichier
    save_documents(documents_db)
    
    return document

@app.get("/documents/{doc_id}", response_model=DocumentResponseEm)
def get_document(doc_id: str):
    document = documents_db.get(doc_id)
    return document

@app.delete("/documents/{doc_id}")
def delete_document(doc_id: str):
    if doc_id not in documents_db:
        raise HTTPException(status_code=404, detail="Document not found")
    
    del documents_db[doc_id]
    
    # Sauvegarder les documents après suppression
    save_documents(documents_db)
    
    return {"message": "Document deleted successfully"}

@app.get("/documents", response_model=List[DocumentResponse])
def list_documents():
    return [DocumentResponse(id=doc.id, content=doc.content) for doc in documents_db.values()]
