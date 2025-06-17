import os
import markdown
from bs4 import BeautifulSoup
from pathlib import Path
import json

# Convert markdown to plain text
def clean_markdown(md_path):
    with open(md_path, 'r', encoding='utf-8') as f:
        html = markdown.markdown(f.read())
    soup = BeautifulSoup(html, 'html.parser')
    return soup.get_text()

# Split text into overlapping chunks
def chunk_text(text, chunk_size=500, overlap=50):
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size - overlap):
        chunk = " ".join(words[i:i + chunk_size])
        chunks.append(chunk)
    return chunks

# Process all markdowns in a folder and save as cleaned JSON
def process_and_save_markdowns(input_dir="markdown_files", output_path="data/cleaned_markdown.json"):
    all_chunks = []
    for file in Path(input_dir).glob("*.md"):
        text = clean_markdown(file)
        chunks = chunk_text(text)
        for i, chunk in enumerate(chunks):
            all_chunks.append({
                "id": f"{file.stem}-{i}",
                "text": chunk,
                "metadata": {
                    "title": file.stem,
                    "source": "markdown"
                }
            })

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(all_chunks, f, indent=2)

    print(f"✅ Saved {len(all_chunks)} markdown chunks to {output_path}")

# Example usage
if __name__ == "__main__":
    process_and_save_markdowns()
