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

    def embed_documents(self, texts):
        """Create consistent mock embeddings for documents"""
        np.random.seed(42)  # For reproducibility
        return [np.random.randn(self.embedding_dim).tolist() for _ in texts]

    def embed_query(self, text: str):
        """Create consistent mock embeddings for query"""
        np.random.seed(42)
        return np.random.randn(self.embedding_dim).tolist()

def load_documents(path):
    docs = []
    for file in os.listdir(path):
        if file.endswith(".txt"):
            loader = TextLoader(os.path.join(path, file), encoding="utf-8")
            docs.extend(loader.load())
    return docs


def split_documents(documents):
    from langchain_text_splitters import CharacterTextSplitter
    splitter = CharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
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