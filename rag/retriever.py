from app.config import VECTOR_DB_PATH
import numpy as np
import faiss
import pickle
import os

def load_db(path):
    """Load the FAISS vector database"""
    index = faiss.read_index(os.path.join(path, "index.faiss"))
    
    with open(os.path.join(path, "index.pkl"), 'rb') as f:
        data = pickle.load(f)
    
    return index, data['documents'], data['embeddings_model']


def retrieve(query, k=5):
    """
    Retrieve relevant documents for a query with improved search
    
    Args:
        query: User's question
        k: Number of documents to retrieve (default: 5)
    
    Returns:
        List of relevant document chunks
    """
    try:
        index, documents, embeddings_model = load_db(VECTOR_DB_PATH)
        
        # Embed the query
        query_embedding = embeddings_model.embed_query(query)
        query_embedding = np.array([query_embedding], dtype='float32')
        
        # Search in FAISS index
        k = min(k, len(documents))  # Don't request more than available
        distances, indices = index.search(query_embedding, k)
        
        # Get the documents
        results = [documents[i] for i in indices[0] if i < len(documents)]
        
        return results
    except Exception as e:
        print(f"Error in retrieval: {e}")
        return []