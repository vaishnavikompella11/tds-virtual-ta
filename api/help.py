'''
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional

app = FastAPI()

class QuestionRequest(BaseModel):
    question: str
    image: Optional[str] = None  # base64 string, optional

@app.post("/api/")
def answer_question(data: QuestionRequest):
    # Placeholder logic
    return {
        "answer": "This is a placeholder answer. Real logic goes here.",
        "links": [
            {
                "url": "https://discourse.onlinedegree.iitm.ac.in/t/example-post",
                "text": "Example related post"
            }
        ]
    }
''' 
from faiss_pipeline import build_index, retrieve, generate_answer

query = "How is bonus shown in dashboard?"

data, index, model = build_index()
results = retrieve(query, index, data, model, top_k=3)
answer = generate_answer(query, [r["combined_text"] for r in results])

print("\n✅ Final Answer:\n", answer)

'''
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional
import sqlite3
import numpy as np
import json
import os
from dotenv import load_dotenv
import requests

load_dotenv()
API_KEY = os.getenv("API_KEY")

app = FastAPI()

# -------------------
# Schema
# -------------------
class QueryRequest(BaseModel):
    question: str
    image: Optional[str] = None  # Not used in logic now

# -------------------
# Utility Functions
# -------------------

def cosine_similarity(a, b):
    a = np.array(a)
    b = np.array(b)
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def embed_text(text: str) -> List[float]:
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "text-embedding-3-small",
        "input": text
    }
    response = requests.post("https://aipipe.org/openai/v1/embeddings", headers=headers, json=data)
    response.raise_for_status()
    return response.json()["data"][0]["embedding"]

# -------------------
# Search Logic
# -------------------

def search_db(embedding: List[float], table: str, top_k: int = 3, threshold: float = 0.4):
    conn = sqlite3.connect("knowledge_base.db")
    cursor = conn.cursor()
    cursor.execute(f"SELECT id, content, embedding FROM {table}")
    rows = cursor.fetchall()
    conn.close()

    scored = []
    for row in rows:
        row_id, content, emb_blob = row
        emb = json.loads(emb_blob)
        score = cosine_similarity(embedding, emb)
        if score > threshold:
            scored.append((score, content, row_id))

    # Sort by similarity
    scored.sort(reverse=True)
    return scored[:top_k]

# -------------------
# API Endpoints
# -------------------

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/query")
def query(data: QueryRequest):
    try:
        user_embedding = embed_text(data.question)

        results = search_db(user_embedding, "markdown_chunks", top_k=2)
        results += search_db(user_embedding, "discourse_chunks", top_k=2)

        # Combine content for GPT
        combined = "\n---\n".join([res[1] for res in results])

        # Prepare final GPT request
        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }
        chat_payload = {
            "model": "gpt-4o-mini",
            "messages": [
                {"role": "system", "content": "You are a helpful teaching assistant. Answer based only on the content given. If nothing matches, say 'I couldn’t find a reliable answer in the content.'"},
                {"role": "user", "content": f"Question: {data.question}\n\nContent:\n{combined}"}
            ]
        }

        chat_response = requests.post("https://aipipe.org/openai/v1/chat/completions", headers=headers, json=chat_payload)
        chat_response.raise_for_status()
        answer = chat_response.json()["choices"][0]["message"]["content"]

        return {
            "answer": answer,
            "sources": [f"Row ID: {res[2]}" for res in results]
        }

    except Exception as e:
        return {"error": str(e)}
'''
