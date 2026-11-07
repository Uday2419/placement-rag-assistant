from retrieval import retrieve_chunks
from generation import generate_answer
from eval_questions import evaluation_questions

for item in evaluation_questions:

    question = item["question"]
    company = item["company"]

    print("\nQuestion:", question)
    print("Expected:", item["expected"])

    chunks = retrieve_chunks(
        question,
        company=company
    )

    if not chunks:
        print("Retrieval: FAILED")
        continue

    print("Retrieval: SUCCESS")

    context = "\n\n".join(
        chunk["text"] for chunk in chunks
    )

    answer = generate_answer(question, context)

    if answer is None:
        print("Generation: FAILED")
    else:
        print("Generated answer:", answer)