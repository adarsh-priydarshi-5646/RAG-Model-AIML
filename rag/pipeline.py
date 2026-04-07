from rag.retriever import retrieve
from rag.generator import generate_answer

def rag_pipeline(query):
    docs = retrieve(query)
    response = generate_answer(query, docs)
    return response