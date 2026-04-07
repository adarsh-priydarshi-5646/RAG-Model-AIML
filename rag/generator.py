from openai import OpenAI
from app.config import OPENAI_API_KEY

def generate_answer(query, docs):
    client = OpenAI(api_key=OPENAI_API_KEY, base_url="https://api.groq.com/openai/v1")

    context = "\n".join([doc.page_content for doc in docs])

    prompt = f"""
    Answer ONLY from the context.
    If not found, say 'I don't know'.

    Context:
    {context}

    Question:
    {query}
    """

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that answers questions based on provided context."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content