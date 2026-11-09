
from query_rewriter import rewrite_query
from document_router import detect_source
from retrieval import retrieve_chunks

question = input("Enter your question: ")

# Rewrite the original question
rewritten_question = rewrite_query(question)

print("\nRewritten question:", rewritten_question)

# Identify the source document
source = detect_source(question)

# Retrieve relevant chunks
results = retrieve_chunks(
    rewritten_question,
    source=source
)

print("\nRetrieved Results:")

for result in results:

    print("\nSource:", result["metadata"].get("source"))
    print("Text:", result["text"])
