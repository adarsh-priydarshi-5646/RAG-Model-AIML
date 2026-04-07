from openai import OpenAI
from app.config import OPENAI_API_KEY
import os

def search_web(query):
    """
    Search web for additional information if needed
    Returns search results as string
    """
    try:
        # Check if we have web search capability
        # For now, return None - can be extended with actual web search API
        return None
    except Exception as e:
        print(f"Web search error: {e}")
        return None


def generate_answer(query, docs, use_web_search=False):
    """
    Generate answer using Groq LLM based on retrieved documents
    
    Args:
        query: User's question
        docs: Retrieved document chunks
        use_web_search: Whether to use web search if answer not found
    
    Returns:
        Generated answer string
    """
    client = OpenAI(api_key=OPENAI_API_KEY, base_url="https://api.groq.com/openai/v1")

    # Check if we have documents
    if not docs:
        if use_web_search:
            return "I couldn't find any relevant information in the documents. For questions outside the document scope, please try rephrasing or adding more documents to the knowledge base."
        return "I couldn't find any relevant information in the documents to answer your question. Please try rephrasing your question or check if the documents contain the information you're looking for."

    # Combine all document content with clear separation
    context_parts = []
    for i, doc in enumerate(docs, 1):
        context_parts.append(f"[Document {i}]\n{doc.page_content}\n")
    
    context = "\n".join(context_parts)

    # Improved prompt with better instructions
    prompt = f"""You are an intelligent assistant helping users find information from documents.

CONTEXT DOCUMENTS:
{context}

USER QUESTION:
{query}

INSTRUCTIONS:
1. Carefully read all the context documents above
2. Answer the question using ONLY the information provided in the context
3. If the exact answer is in the documents, provide it clearly and concisely
4. If the information is partially available, provide what you can find and mention what's missing
5. If the answer is not in the documents at all, clearly state: "I don't have enough information in the provided documents to answer this question."
6. Be specific and cite which document(s) contain the information when relevant
7. Use natural, conversational language
8. If multiple documents contain related information, synthesize them into a coherent answer

ANSWER:"""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system", 
                    "content": "You are a knowledgeable and helpful assistant. You provide accurate, well-structured answers based on given context. You are honest about limitations and always cite your sources when possible."
                },
                {
                    "role": "user", 
                    "content": prompt
                }
            ],
            temperature=0.2,  # Very low for factual accuracy
            max_tokens=1500,  # Allow comprehensive answers
            top_p=0.9,
            frequency_penalty=0.0,
            presence_penalty=0.0
        )
        
        answer = response.choices[0].message.content
        
        # Clean up the answer
        answer = answer.strip()
        
        # Check if answer indicates information not found
        not_found_phrases = [
            "don't have enough information",
            "not in the documents",
            "cannot find",
            "not mentioned in the context"
        ]
        
        if use_web_search and any(phrase in answer.lower() for phrase in not_found_phrases):
            # Add note about web search capability
            answer += "\n\nNote: This answer is based only on the provided documents. For broader information, consider adding more relevant documents to the knowledge base."
        
        return answer
        
    except Exception as e:
        error_message = f"Error generating answer: {str(e)}"
        print(error_message)
        return f"I encountered an error while generating the answer. Please try again. Error details: {str(e)}"