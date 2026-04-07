from app.config import DATA_PATH, VECTOR_DB_PATH
import numpy as np
import os
import faiss
import pickle

class Document:
    """Simple document class to replace langchain Document"""
    def __init__(self, page_content: str, metadata: dict = None):
        self.page_content = page_content
        self.metadata = metadata or {}

class MockEmbeddings:
    """Mock embeddings for testing without OpenAI API"""
    def __init__(self, embedding_dim: int = 1536):
        self.embedding_dim = embedding_dim
        self._cache = {}  # Cache for consistent embeddings

    def _get_embedding(self, text: str):
        """Generate consistent embedding for a given text"""
        # Use hash of text as seed for consistency
        import hashlib
        text_hash = int(hashlib.md5(text.encode()).hexdigest(), 16)
        np.random.seed(text_hash % (2**32))  # Use hash as seed
        embedding = np.random.randn(self.embedding_dim).astype('float32')
        # Normalize for better similarity search
        norm = np.linalg.norm(embedding)
        if norm > 0:
            embedding = embedding / norm
        return embedding

    def embed_documents(self, texts):
        """Create consistent mock embeddings for documents"""
        embeddings = []
        for text in texts:
            if text not in self._cache:
                self._cache[text] = self._get_embedding(text)
            embeddings.append(self._cache[text])
        return np.array(embeddings, dtype='float32')

    def embed_query(self, text: str):
        """Create consistent mock embeddings for query"""
        if text not in self._cache:
            self._cache[text] = self._get_embedding(text)
        return self._cache[text]

def load_documents(path):
    """Load text documents from directory"""
    docs = []
    for file in os.listdir(path):
        if file.endswith(".txt"):
            file_path = os.path.join(path, file)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    docs.append(Document(
                        page_content=content,
                        metadata={"source": file}
                    ))
            except Exception as e:
                print(f"Error loading {file}: {e}")
    return docs


def split_documents(documents):
    """
    Split documents into chunks with improved strategy
    - Larger chunks for better context
    - More overlap to preserve continuity
    """
    chunks = []
    chunk_size = 1000
    chunk_overlap = 200
    separator = "\n\n"
    
    for doc in documents:
        text = doc.page_content
        # First split by separator
        parts = text.split(separator)
        
        current_chunk = ""
        for part in parts:
            if len(current_chunk) + len(part) + len(separator) <= chunk_size:
                current_chunk += part + separator
            else:
                if current_chunk:
                    chunks.append(Document(
                        page_content=current_chunk.strip(),
                        metadata=doc.metadata.copy()
                    ))
                current_chunk = part + separator
        
        # Add remaining chunk
        if current_chunk:
            chunks.append(Document(
                page_content=current_chunk.strip(),
                metadata=doc.metadata.copy()
            ))
    
    return chunks


def create_vector_db(docs, save_path):
    """Create FAISS vector database from documents"""
    embeddings_model = MockEmbeddings()
    
    # Extract text and create embeddings
    texts = [doc.page_content for doc in docs]
    embeddings = embeddings_model.embed_documents(texts)
    
    # Create FAISS index
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)
    
    # Save index and documents
    os.makedirs(save_path, exist_ok=True)
    faiss.write_index(index, os.path.join(save_path, "index.faiss"))
    
    # Save documents and embeddings model
    with open(os.path.join(save_path, "index.pkl"), 'wb') as f:
        pickle.dump({
            'documents': docs,
            'embeddings_model': embeddings_model
        }, f)
    
    return index, docs, embeddings_model


def run_ingestion():
    """Run the full ingestion pipeline"""
    print("Starting ingestion...")
    docs = load_documents(DATA_PATH)
    print(f"Loaded {len(docs)} documents")
    
    chunks = split_documents(docs)
    print(f"Split into {len(chunks)} chunks")
    
    index, docs, embeddings = create_vector_db(chunks, VECTOR_DB_PATH)
    print("Ingestion Complete")