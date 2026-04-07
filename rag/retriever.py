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
    Retrieve relevant documents for a query with improved search
    
    Args:
        query: User's question
        k: Number of documents to retrieve (default: 3)
    
    Returns:
        List of relevant document chunks
    """
    try:
        db = load_db(VECTOR_DB_PATH)
        
        # Get more results initially for better coverage
        initial_k = min(k * 2, 10)  # Get double but cap at 10
        
        # Use similarity search with score
        results_with_scores = db.similarity_search_with_score(query, k=initial_k)
        
        # Filter by relevance score if available
        if results_with_scores:
            # Sort by score (lower is better for FAISS)
            results_with_scores.sort(key=lambda x: x[1])
            
            # Take top k results
            results = [doc for doc, score in results_with_scores[:k]]
        else:
            # Fallback to regular search
            results = db.similarity_search(query, k=k)
        
        # If still no results, try with relaxed search
        if not results:
            results = db.similarity_search(query, k=k*2)
        
        return results
    except Exception as e:
        print(f"Error in retrieval: {e}")
        return []