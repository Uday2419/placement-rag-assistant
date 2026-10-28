
from retrieval import retrieve_chunks

question = "What is the CGPA requirement for Company X?"

chunks = retrieve_chunks(
    question,
    company="Company X",
)

if not chunks:
    print("No chunks retrieved.")
else:
    for chunk in chunks:
        print("Text:", chunk["text"])
        print("Metadata:", chunk["metadata"])
        print("Distance:", chunk["distance"])
        print("-" * 40)
