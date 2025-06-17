#huhhhhhhhhhhhhhhhhhhhh

import os
import json
import openai
import chromadb
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# ✅ Updated: Use new Chroma client
client = chromadb.HttpClient(host="localhost", port=8000)
collection = client.get_or_create_collection("tds-content")

# 1. Load markdown files
def load_markdown(folder="markdown_files"):
    data = []
    for fname in os.listdir(folder):
        if fname.endswith(".md"):
            with open(os.path.join(folder, fname), "r", encoding="utf-8") as f:
                content = f.read()
                data.append({"id": fname, "text": content})
    return data

# 2. Load JSON posts
def load_json(file="data/tds_discourse_data.json"):
    data = []
    with open(file, "r", encoding="utf-8") as f:
        json_data = json.load(f)
        for i, topic in enumerate(json_data):
            for j, post in enumerate(topic["posts"]):
                data.append({
                    "id": f"{i}-{j}",
                    "text": post["content"],
                })
    return data

# 3. Embed and store
def embed_and_store():
    all_data = load_markdown() + load_json()
    for doc in all_data:
        collection.add(
            documents=[doc["text"]],
            metadatas=[{"source": doc["id"]}],
            ids=[doc["id"]]
        )
    print(f"✅ Embedded and stored {len(all_data)} items in Chroma.")

if __name__ == "__main__":
    embed_and_store()
