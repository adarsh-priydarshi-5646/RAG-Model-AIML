from openai import OpenAI
from app.config import OPENAI_API_KEY

def generate_answer(query, docs):
    client = OpenAI(api_key=OPENAI_API_KEY, base_url="https://api.groq.com/openai/v1")

    # Combine all document content
    context = "\n\n".join([f"Document {i+1}:\n{doc.page_content}" for i, doc in enumerate(docs)])

    # Improved prompt with better instructions
    prompt = f"""You are a helpful AI assistant. Your task is to answer questions based on the provided context documents.

INSTRUCTIONS:
1. Read the context carefully
2. Answer the question using ONLY information from the context
3. If the answer is not in the context, say "I don't have enough information to answer this question based on the provided documents."
4. Be specific and detailed in your answer
5. If relevant, mention which part of the context supports your answer
6. Use a natural, conversational tone

CONTEXT:
{context}

QUESTION:
{query}

ANSWER:"""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system", 
                    "content": "You are a knowledgeable assistant that provides accurate answers based on given context. You are helpful, precise, and honest. If you don't know something, you admit it."
                },
                {
                    "role": "user", 
                    "content": prompt
                }
            ],
            temperature=0.3,  # Lower temperature for more focused answers
            max_tokens=1000,  # Allow longer responses
            top_p=0.9
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error generating answer: {str(e)}"