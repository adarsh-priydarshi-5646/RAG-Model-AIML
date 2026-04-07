from langchain_community.vectorstores import FAISS
from rag.ingestion import MockEmbeddings
from app.config import VECTOR_DB_PATH

def load_db(path):
    embeddings = MockEmbeddings()
    db = FAISS.load_local(path, embeddings, allow_dangerous_deserialization=True)
    return db


def retrieve(query, k=3):
    db = load_db(VECTOR_DB_PATH)
    results = db.similarity_search(query, k=k)
    return results