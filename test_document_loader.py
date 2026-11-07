from document_loader import load_documents

documents = load_documents()

print("Total documents:", len(documents))

for document in documents:

    print("\nSource:", document["source"])

    print("Content:")
    print(document["text"])