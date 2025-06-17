import os
import json
import sqlite3
import aiohttp
import asyncio
import textwrap
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("OPENAI_API_KEY")

DB_PATH = "knowledge_base.db"
MARKDOWN_FOLDER = "markdown_files"
DISCOURSE_FILE = "data/tds_discourse_data.json"

# Split text into clean ~500-character chunks
def chunk_text(text, chunk_size=500):
    return textwrap.wrap(text, width=chunk_size, break_long_words=False, replace_whitespace=False)

# Get embedding using AI Pipe proxy
async def get_embedding(text):
    url = "https://aipipe.org/openai/v1/embeddings"  # ✅ correct AI Pipe proxy URL
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "text-embedding-3-small",
        "input": text
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=payload) as response:
            print(f"Status: {response.status}")
            print(f"Content-Type: {response.headers.get('Content-Type')}")
            raw_text = await response.text()
            print(f"Raw response: {raw_text[:300]}")  # print part of response to debug

            if response.status == 200 and "application/json" in response.headers.get("Content-Type", ""):
                result = json.loads(raw_text)
                return result["data"][0]["embedding"]
            else:
                raise Exception(f"❌ Failed to get embedding:\n{raw_text}")


# Store markdown chunks
async def process_markdown(conn):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM markdown_chunks")

    for fname in os.listdir(MARKDOWN_FOLDER):
        if not fname.endswith(".md"):
            continue
        path = os.path.join(MARKDOWN_FOLDER, fname)
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()
        chunks = chunk_text(text)
        for i, chunk in enumerate(chunks):
            embedding = await get_embedding(chunk)
            cursor.execute("""
                INSERT INTO markdown_chunks (doc_title, original_url, downloaded_at, chunk_index, content, embedding)
                VALUES (?, ?, datetime('now'), ?, ?, ?)
            """, (fname, f"https://tds.s-anand.net/#/2025-01/{fname}", i, chunk, json.dumps(embedding)))
    conn.commit()
    print("✅ Markdown chunks inserted.")

# Store discourse chunks
async def process_discourse(conn):
    with open(DISCOURSE_FILE, "r", encoding="utf-8") as f:
        discourse = json.load(f)

    cursor = conn.cursor()

    for i, post in enumerate(discourse):
        content = post["content"]
        chunks = chunk_text(content)
        for j, chunk in enumerate(chunks):
            embedding = await get_embedding(chunk)
            cursor.execute("""
                INSERT INTO discourse_chunks (
                    post_id, topic_id, topic_title, post_number, author, created_at,
                    likes, chunk_index, content, url, embedding
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                post["post_id"],
                post["topic_id"],
                post["topic_title"],
                post["post_number"],
                post["author"],
                post["created_at"],
                post["like_count"],
                j,
                chunk,
                post["url"],
                json.dumps(embedding)
            ))

    conn.commit()
    print("✅ Discourse chunks inserted.")


# Main runner
async def main():
    if not API_KEY:
        print("❌ API_KEY not set in .env")
        return
    conn = sqlite3.connect(DB_PATH)
    
    await process_discourse(conn)

    await process_markdown(conn)
    print("✅ All data processed and stored in database.")
    conn.close()

if __name__ == "__main__":
    asyncio.run(main())
