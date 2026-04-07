from rag.retriever import retrieve
from rag.generator import generate_answer

def rag_pipeline(query, k=5):
    """
    Complete RAG pipeline
    
    Args:
        query: User's question
        k: Number of documents to retrieve (default: 5 for better coverage)
    
    Returns:
        Generated answer
    """
    docs = retrieve(query, k=k)
    response = generate_answer(query, docs)
    return response