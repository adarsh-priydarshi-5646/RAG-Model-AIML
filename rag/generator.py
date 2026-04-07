from openai import OpenAI
from app.config import OPENAI_API_KEY
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.web_search import web_search, format_search_results


def generate_answer(query, docs, use_web_search=True):
    """
    Generate answer using Groq LLM based on retrieved documents
    Falls back to web search if answer not found in documents
    
    Args:
        query: User's question
        docs: Retrieved document chunks
        use_web_search: Whether to use web search if answer not found (default: True)
    
    Returns:
        Generated answer string
    """
    client = OpenAI(api_key=OPENAI_API_KEY, base_url="https://api.groq.com/openai/v1")

    # Combine all document content with clear separation
    context_parts = []
    has_documents = docs and len(docs) > 0
    
    if has_documents:
        for i, doc in enumerate(docs, 1):
            context_parts.append(f"[Document {i}]\n{doc.page_content}\n")
        context = "\n".join(context_parts)
    else:
        context = "No relevant documents found in the knowledge base."

    # First attempt: Try to answer from documents
    prompt = f"""You are an intelligent assistant helping users find information.

CONTEXT FROM KNOWLEDGE BASE:
{context}

USER QUESTION:
{query}

INSTRUCTIONS:
1. Carefully read the context from the knowledge base
2. If the answer is clearly in the context, provide it with confidence
3. If the answer is NOT in the context or context is insufficient, respond with exactly: "NEED_WEB_SEARCH"
4. Be specific and cite which document(s) contain the information when relevant
5. Use natural, conversational language

ANSWER:"""

    try:
        # First attempt with documents
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system", 
                    "content": "You are a knowledgeable assistant. If information is not in the provided context, respond with 'NEED_WEB_SEARCH'."
                },
                {
                    "role": "user", 
                    "content": prompt
                }
            ],
            temperature=0.2,
            max_tokens=1500,
            top_p=0.9
        )
        
        answer = response.choices[0].message.content.strip()
        
        # Check if we need web search
        needs_web_search = (
            "NEED_WEB_SEARCH" in answer or
            "don't have enough information" in answer.lower() or
            "not in the documents" in answer.lower() or
            "not mentioned" in answer.lower()
        )
        
        if needs_web_search and use_web_search:
            print(f"Performing web search for: {query}")
            
            # Perform web search
            search_results = web_search(query, max_results=3)
            
            if search_results:
                # Format search results
                web_context = format_search_results(search_results)
                
                # Generate answer with web search results
                web_prompt = f"""You are an intelligent assistant helping users find information.

CONTEXT FROM KNOWLEDGE BASE:
{context}

WEB SEARCH RESULTS:
{web_context}

USER QUESTION:
{query}

INSTRUCTIONS:
1. First check if the knowledge base has the answer
2. If not, use the web search results to answer the question
3. Provide a clear, accurate answer based on the available information
4. Cite your sources (mention if from knowledge base or web search)
5. If information is from web search, mention the source URL
6. Be honest if you still cannot find a good answer

ANSWER:"""

                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {
                            "role": "system", 
                            "content": "You are a helpful assistant that provides accurate answers from knowledge base or web search results. Always cite your sources."
                        },
                        {
                            "role": "user", 
                            "content": web_prompt
                        }
                    ],
                    temperature=0.3,
                    max_tokens=2000,
                    top_p=0.9
                )
                
                answer = response.choices[0].message.content.strip()
                answer += "\n\n[Note: This answer includes information from web search]"
            else:
                answer = "I couldn't find enough information in the knowledge base, and web search didn't return useful results. Please try rephrasing your question or add more documents to the knowledge base."
        
        return answer
        
    except Exception as e:
        error_message = f"Error generating answer: {str(e)}"
        print(error_message)
        return f"I encountered an error while generating the answer. Please try again. Error details: {str(e)}"