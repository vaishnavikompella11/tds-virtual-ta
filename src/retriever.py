import chromadb

client = chromadb.PersistentClient(path="chroma_db/")

collection = client.get_collection("tds-rag")  # Use existing collection

def retrieve_top_k(query: str, k: int = 5):
    results = collection.query(query_texts=[query], n_results=k)

    # Returns [(text, metadata)...]
    return list(zip(results["documents"][0], results["metadatas"][0]))
