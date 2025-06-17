import requests

def generate_answer(question, context, token):
    headers = {"Authorization": f"Bearer {token}"}
    prompt = f"""
You are a helpful TA. Use the context below to answer clearly.

Context:
{context}

Question:
{question}




Answer:"""

    try:
        response = requests.post(
            "https://aipipe.org/openrouter/v1/chat/completions",
            headers=headers,
            json={
                "model": "gpt-3.5-turbo",
                "prompt": prompt
            }
        )

        print("🔁 AIPipe raw response:", response.text)

        if response.status_code != 200:
            return f"❌ AIPipe Error: {response.status_code} - {response.text}"

        data = response.json()
        return data["choices"][0]["text"].strip()

    except Exception as e:
        print(f"❌ AIPipe request failed: {e}")
        return f"❌ AIPipe request failed: {str(e)}"
