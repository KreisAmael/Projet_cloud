from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import uuid
import numpy as np
from sentence_transformers import SentenceTransformer
from scipy.spatial.distance import cosine
from transformers import pipeline

app = FastAPI()

# In-memory storage for documents (replace with a database in production)
documents_db = {}

# Load the embedding model
embedding_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

# Load a lightweight text generation model
generation_pipeline = pipeline("text2text-generation", model="t5-small")

# Document model
class Document(BaseModel):
    id: str
    content: str
    embedding: List[float]

# Response model for document retrieval (without embedding)
class DocumentResponse(BaseModel):
    id: str
    content: str

# Request model for adding documents
class DocumentCreate(BaseModel):
    content: str

# Request model for query embeddings
class Query(BaseModel):
    query_text: str

# Request model for response generation
class GenerationRequest(BaseModel):
    query_text: str
    documents: List[str]

@app.post("/documents", response_model=Document)
def add_document(doc: DocumentCreate):
    """Add a new document."""
    # Generate embedding for the document content
    embedding = embedding_model.encode(doc.content).tolist()
    
    # Create a unique ID and store the document
    doc_id = str(uuid.uuid4())
    document = Document(id=doc_id, content=doc.content, embedding=embedding)
    documents_db[doc_id] = document
    return document

@app.get("/documents/{doc_id}", response_model=DocumentResponse)
def get_document(doc_id: str):
    """Retrieve a document by ID without returning embeddings."""
    document = documents_db.get(doc_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    return DocumentResponse(id=document.id, content=document.content)

@app.delete("/documents/{doc_id}")
def delete_document(doc_id: str):
    """Delete a document by ID."""
    if doc_id not in documents_db:
        raise HTTPException(status_code=404, detail="Document not found")
    del documents_db[doc_id]
    return {"message": "Document deleted successfully"}

@app.get("/documents", response_model=List[DocumentResponse])
def list_documents():
    """List all documents without embeddings."""
    return [DocumentResponse(id=doc.id, content=doc.content) for doc in documents_db.values()]

@app.post("/query_embedding")
def generate_query_embedding(query: Query):
    """Generate an embedding for the given query text."""
    embedding = embedding_model.encode(query.query_text).tolist()
    return {"query_text": query.query_text, "embedding": embedding}

@app.post("/retrieve_documents")
def retrieve_documents(query: Query, top_k: int = 5):
    """Retrieve the top-k most relevant documents based on cosine similarity."""
    if not documents_db:
        raise HTTPException(status_code=404, detail="No documents available")

    # Generate embedding for the query
    query_embedding = np.array(embedding_model.encode(query.query_text))

    # Calculate cosine similarity with all documents
    similarities = []
    for doc_id, doc in documents_db.items():
        doc_embedding = np.array(doc.embedding)
        similarity = 1 - cosine(query_embedding, doc_embedding)
        similarities.append((doc, similarity))

    # Sort documents by similarity
    similarities = sorted(similarities, key=lambda x: x[1], reverse=True)
    top_documents = [doc for doc, _ in similarities[:top_k]]

    return {"query_text": query.query_text, "top_documents": top_documents}

@app.post("/generate_response")
def generate_response(request: GenerationRequest):
    """Generate a response based on the query and relevant documents."""
    if not request.documents:
        raise HTTPException(status_code=400, detail="No documents provided")

    # Combine documents into a single context
    context = "\n".join(request.documents)

    # Generate a response using the text generation pipeline
    prompt = f"Query: {request.query_text}\nContext: {context}\nAnswer:"
    response = generation_pipeline(prompt, max_length=100, num_return_sequences=1)[0]['generated_text']

    return {"query_text": request.query_text, "response": response}
