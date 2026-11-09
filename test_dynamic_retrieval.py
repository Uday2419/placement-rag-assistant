
from document_router import detect_source
from retrieval import retrieve_chunks

question = input("Enter your question: ")

source = detect_source(question)

results = retrieve_chunks(
    question,
    source=source
)

for result in results:

    print("\nSource:", result["metadata"].get("source"))
    print("Text:", result["text"])
