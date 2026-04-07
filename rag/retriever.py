from langchain_community.vectorstores import FAISS
from rag.ingestion import MockEmbeddings
from app.config import VECTOR_DB_PATH

def load_db(path):
    """Load the FAISS vector database"""
    embeddings = MockEmbeddings()
    db = FAISS.load_local(path, embeddings, allow_dangerous_deserialization=True)
    return db


def retrieve(query, k=3):
    """
    Retrieve relevant documents for a query
    
    Args:
        query: User's question
        k: Number of documents to retrieve (default: 3)
    
    Returns:
        List of relevant document chunks
    """
    try:
        db = load_db(VECTOR_DB_PATH)
        
        # Use similarity search with score to get most relevant docs
        results = db.similarity_search(query, k=k)
        
        # If no results, try with more relaxed search
        if not results:
            results = db.similarity_search(query, k=k*2)
        
        return results
    except Exception as e:
        print(f"Error in retrieval: {e}")
        return []