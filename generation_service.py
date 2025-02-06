from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from transformers import T5Tokenizer, T5ForConditionalGeneration

app = FastAPI()

tokenizer = T5Tokenizer.from_pretrained("t5-small")
model = T5ForConditionalGeneration.from_pretrained("t5-small")

# Modèles pour la requête et la liste des documents
class GenerationInput(BaseModel):
    query: str
    documents: list[dict]

@app.post("/generate_response")
async def generate_response(input_data: GenerationInput):
    context = " ".join([doc["content"] for doc in input_data.documents])

    input_text = f"Use the context to anser the question, question: {input_data.query} context: {context}"
    print(input_text)
    inputs = tokenizer(input_text, return_tensors="pt", truncation=True, max_length=512)

    outputs = model.generate(
    input_ids=inputs["input_ids"],
    attention_mask=inputs["attention_mask"],
    max_length=250,
    repetition_penalty=2.0,
    length_penalty=1.5,
    num_beams=5
    )

    response = tokenizer.decode(outputs[0], skip_special_tokens=True)

    return {"response": response}
