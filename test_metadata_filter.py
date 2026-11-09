from retrieval import retrieve_chunks

question = input("Enter your question: ")

source = input("Enter source filename: ")

results = retrieve_chunks(
    question,
    source=source
)

print("\nFiltered Results:")

for result in results:

    print("\nSource:",
          result["metadata"].get("source"))

    print("Text:", result["text"])

    print("Distance:", result["distance"])