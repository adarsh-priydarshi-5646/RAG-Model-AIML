from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import CharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain.embeddings.base import Embeddings
from app.config import DATA_PATH, VECTOR_DB_PATH
import numpy as np
import os

class MockEmbeddings(Embeddings):
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
        embedding = np.random.randn(self.embedding_dim).tolist()
        return embedding

    def embed_documents(self, texts):
        """Create consistent mock embeddings for documents"""
        embeddings = []
        for text in texts:
            if text not in self._cache:
                self._cache[text] = self._get_embedding(text)
            embeddings.append(self._cache[text])
        return embeddings

    def embed_query(self, text: str):
        """Create consistent mock embeddings for query"""
        if text not in self._cache:
            self._cache[text] = self._get_embedding(text)
        return self._cache[text]

def load_documents(path):
    docs = []
    for file in os.listdir(path):
        if file.endswith(".txt"):
            loader = TextLoader(os.path.join(path, file), encoding="utf-8")
            docs.extend(loader.load())
    return docs


def split_documents(documents):
    """
    Split documents into chunks with improved strategy
    - Larger chunks for better context
    - More overlap to preserve continuity
    """
    from langchain_text_splitters import CharacterTextSplitter
    splitter = CharacterTextSplitter(
        chunk_size=1000,      # Increased from 500 for better context
        chunk_overlap=200,    # Increased from 50 for better continuity
        separator="\n\n"      # Split on paragraphs first
    )
    return splitter.split_documents(documents)


def create_vector_db(docs, save_path):
    embeddings = MockEmbeddings()
    db = FAISS.from_documents(docs, embeddings)
    db.save_local(save_path)
    return db


def run_ingestion():
    docs = load_documents(DATA_PATH)
    chunks = split_documents(docs)
    db = create_vector_db(chunks, VECTOR_DB_PATH)
    print("✅ Ingestion Complete")