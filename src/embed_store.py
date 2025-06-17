import json
import chromadb
from chromadb.utils import embedding_functions

# Step 1: Load cleaned markdown and discourse data
def load_data():
    with open("data/clean/cleaned_markdown.json", "r", encoding="utf-8") as f:
        markdown_chunks = json.load(f)

    with open("data/clean/cleaned_discourse.json", "r", encoding="utf-8") as f:
        discourse_chunks = json.load(f)

    all_chunks = markdown_chunks + discourse_chunks

    # Step 2: Fix metadata (Chroma does not support lists)
    for chunk in all_chunks:
        meta = chunk["metadata"]
        if "tags" in meta and isinstance(meta["tags"], list):
            meta["tags"] = ", ".join(meta["tags"])  # Convert list to string
        chunk["metadata"] = meta

    return all_chunks

# Step 3: Use local embedding model
embed_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)

# Step 4: Initialize ChromaDB client
client = chromadb.PersistentClient(path="chroma_db/")

collection = client.get_or_create_collection(
    name="tds-rag",
    embedding_function=embed_fn
)

# Step 5: Load and add data
all_chunks = load_data()

collection.add(
    documents=[chunk["text"] for chunk in all_chunks],
    metadatas=[chunk["metadata"] for chunk in all_chunks],
    ids=[chunk["id"] for chunk in all_chunks]
)

print(f"✅ Successfully embedded and stored {len(all_chunks)} chunks in ChromaDB.")
