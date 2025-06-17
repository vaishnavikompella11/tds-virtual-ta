
from fastapi import FastAPI
from pydantic import BaseModel
from src.retriever import retrieve_top_k
from src.generator import generate_answer
from dotenv import load_dotenv
import os

import base64
from io import BytesIO
from PIL import Image
import pytesseract


load_dotenv()

# ⬇️ Set your token here
AIPIPE_TOKEN = os.getenv("API_KEY")
app = FastAPI()

# 👇 JSON input schema
class QuestionInput(BaseModel):
    question: str
    image: str | None = None  # base64-encoded image

# 👇 JSON output schema
class AnswerOutput(BaseModel):
    answer: str
    links: list[dict]  # {"text": ..., "url": ...}

@app.get("/")
def root():
    return {"message": "TDS Virtual TA is live!"}

@app.post("/api/", response_model=AnswerOutput)
def handle_query(input: QuestionInput):
    question = input.question
    image_text = ""

    # 🔍 Step 0: Extract text from base64 image if provided
    if input.image:
        try:
            image_data = base64.b64decode(input.image)
            image = Image.open(BytesIO(image_data))
            image_text = pytesseract.image_to_string(image, lang="eng+jpn")
        except Exception as e:
            image_text = f"[OCR Failed: {str(e)}]"

    # 🔀 Step 1: Combine question + image text
    full_question = question
    if image_text:
        full_question += f"\n\n[Image Text Extracted via OCR:]\n{image_text.strip()}"

    # 🔎 Step 2: Retrieve relevant chunks
    chunks = retrieve_top_k(full_question, k=5)

    # 📚 Step 3: Build context string
    context = "\n\n".join([c[0] for c in chunks])

    # 🤖 Step 4: Generate answer with AIPipe
    answer = generate_answer(full_question, context, AIPIPE_TOKEN)

    # 🔗 Step 5: Return with metadata links
    links = []
    for text, meta in chunks:
        url = meta.get("url")
        if url:
            links.append({"text": meta.get("title", "Related"), "url": url})

    return {"answer": answer, "links": links}
