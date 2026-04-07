from rag.pipeline import rag_pipeline

if __name__ == "__main__":
    while True:
        query = input("Ask something: ")
        if query.lower() == "exit":
            break

        answer = rag_pipeline(query)
        print("\n🤖 Answer:", answer)