from retrieval import retrieve_chunks

question = input("Enter your question: ")

results = retrieve_chunks(question)

print("\nRetrieved Results:")

for result in results:

    print("\nSource:",
          result["metadata"].get("source"))

    print("Text:", result["text"])

    print("Distance:", result["distance"])