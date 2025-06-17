import json

def clean_discourse_json(in_path, out_path):
    with open(in_path, 'r', encoding='utf-8') as f:
        posts = json.load(f)

    cleaned = []
    for post in posts:
        content = post.get("content", "").strip()
        if not content:
            continue

        cleaned.append({
            "id": f"disc-{post['topic_id']}-{post['post_number']}",
            "text": content,
            "metadata": {
                "title": post.get("topic_title", ""),
                "url": post.get("url", ""),
                "tags": post.get("tags", [])
            }
        })

    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(cleaned, f, indent=2)

# Run it like:
clean_discourse_json("data/discourse_posts.json", "data/cleaned_discourse.json")
