from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests

app = FastAPI()

class UserQuery(BaseModel):
    query_text: str

class UserResponse(BaseModel):
    response: str

# Configuration des URLs des microservices
DOCUMENTS_SERVICE_URL = "http://documents-service:8000" #"http://127.0.0.1:8000"
RETRIEVE_URL = "http://retrieval-service:8001" #"http://127.0.0.1:8001"
GENERATE_URL = "http://generation-service:8002" #"http://127.0.0.1:8002"

# Fonction pour ajouter un document
@app.post("/add_document")
def add_document(content: str):
    url = f"{DOCUMENTS_SERVICE_URL}/documents"
    payload = {"content": content}
    response = requests.post(url, json=payload)
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Failed to add document")
    return response.json()

# Fonction pour lister tous les documents
@app.get("/list_documents")
def list_documents():
    url = f"{DOCUMENTS_SERVICE_URL}/documents"
    response = requests.get(url)
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Failed to list documents")
    return response.json()

# Fonction pour supprimer un document par son ID
@app.delete("/delete_document/{doc_id}")
def delete_document(doc_id: str):
    url = f"{DOCUMENTS_SERVICE_URL}/documents/{doc_id}"
    response = requests.delete(url)
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Failed to delete document")
    return response.json()

@app.post("/retrieve")
def call_retrieve(user_query: UserQuery):
    url = f"{RETRIEVE_URL}/retrieve_documents"
    response = requests.post(url, json={"query_text": user_query.query_text})
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Retrieve service failed")
    return response.json()

@app.post("/process_query")
async def process_query(user_query: UserQuery):
    url = f"{RETRIEVE_URL}/retrieve_documents"

    retrieve_response = requests.post(url, json={"query_text": user_query.query_text})
    if retrieve_response.status_code != 200:
        raise HTTPException(status_code=retrieve_response.status_code, detail="Retrieve service failed")

    documents = retrieve_response.json()

    generate_payload = {
        "query": user_query.query_text,
        "documents": documents
    }

    url2 = f"{GENERATE_URL}/generate_response"

    generate_response = requests.post(url2, json=generate_payload)
    if generate_response.status_code != 200:
        raise HTTPException(status_code=generate_response.status_code, detail="Generate service failed")

    generated_response = generate_response.json()
    return generated_response