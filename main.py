from retrieval import retrieve_chunks
from generation import generate_answer 





from config import (
    DATA_FILE,
    CHROMA_DB_PATH,
    COLLECTION_NAME,
    EMBEDDING_MODEL,
    LLM_MODEL,
    TOP_K,
)

from pathlib import Path
from time import perf_counter
import re

import chromadb
import ollama
from sentence_transformers import SentenceTransformer


# --------------------------------------------------
# 1. Load the embedding model
# --------------------------------------------------

start = perf_counter()
print("Loading embedding model...")

embedding_model = SentenceTransformer(
    EMBEDDING_MODEL
)

print(f"Model loading: {perf_counter() - start:.2f} seconds")


# --------------------------------------------------
# 2. Read and split the placement document
# --------------------------------------------------

file_path = Path(__file__).parent / "data" / "placement.txt"

if not file_path.exists():
    raise FileNotFoundError(
        f"Placement document not found: {file_path}"
    )

text = file_path.read_text(encoding="utf-8")

documents = [
    paragraph.strip()
    for paragraph in text.split("\n\n")
    if paragraph.strip()
]

if not documents:
    raise ValueError("placement.txt contains no documents.")

print(f"Document chunks: {len(documents)}")


# --------------------------------------------------
# 3. Create persistent ChromaDB client
# --------------------------------------------------

db_path = Path(__file__).parent / "chroma_db"

db_client = chromadb.PersistentClient(
    path=str(db_path)
)

collection_name = COLLECTION_NAME
# Set True for ONE run if you need to rebuild
# the existing index. Then change it back to False.
REBUILD_INDEX = False

existing_collections = [
    collection.name
    for collection in db_client.list_collections()
]

if REBUILD_INDEX and collection_name in existing_collections:
    db_client.delete_collection(name=collection_name)
    print("Old collection deleted.")


# --------------------------------------------------
# 4. Create or load the collection
# --------------------------------------------------

collection = db_client.get_or_create_collection(
    name=collection_name
)

if collection.count() == 0:
    print("Creating document embeddings...")

    start = perf_counter()

    document_vectors = embedding_model.encode(
        documents
    ).tolist()

    metadatas = []

    for i, document in enumerate(documents):
        if "Company X" in document:
            company = "Company X"
        elif "Company Y" in document:
            company = "Company Y"
        else:
            company = "General"

        metadatas.append({
            "source": "placement.txt",
            "chunk_number": i,
            "company": company
        })

    collection.add(
        ids=[f"chunk_{i}" for i in range(len(documents))],
        documents=documents,
        embeddings=document_vectors,
        metadatas=metadatas
    )

    print(
        f"Embedding and storage: "
        f"{perf_counter() - start:.2f} seconds"
    )
else:
    print("Using saved document embeddings.")

print(f"Stored records: {collection.count()}")


# --------------------------------------------------
# 5. Identify company mentioned in the question
# --------------------------------------------------

def detect_company(question):
    question_lower = question.lower()

    has_x = re.search(r"\bcompany\s+x\b", question_lower)
    has_y = re.search(r"\bcompany\s+y\b", question_lower)

    if has_x and not has_y:
        return "Company X"

    if has_y and not has_x:
        return "Company Y"

    return None


# --------------------------------------------------
# 6. Answer strict eligibility questions with rules
# --------------------------------------------------

def answer_eligibility_question(question):
    question_lower = question.lower()
    company = detect_company(question)

    if company is None:
        return None

    # Only handle questions about CGPA, backlogs,
    # or eligibility. Other questions go to the LLM.
    keywords = [
        "cgpa", "backlog", "backlogs",
        "eligible", "eligibility",
        "qualify", "qualification",
        "apply", "requirement", "requirements"
    ]

    if not any(word in question_lower for word in keywords):
        return None

    # These rules must match placement.txt.
    if company == "Company X":
        required_cgpa = 7.5
        max_backlogs = 0
    else:
        required_cgpa = 8.0
        max_backlogs = 1

    # Questions about the CGPA requirement.
    if "cgpa" in question_lower and not any(
        word in question_lower
        for word in ["eligible", "apply", "qualify"]
    ):
        return (
            f"{company} requires a CGPA above "
            f"{required_cgpa:.1f}."
        )

    # Questions about the backlog policy.
    asks_backlog_policy = (
        "backlog" in question_lower
        or "backlogs" in question_lower
    )

    is_policy_question = any(
        phrase in question_lower
        for phrase in [
            "allow", "allows", "allowed",
            "requirement", "requirements",
            "can students", "must have",
            "active backlog"
        ]
    )

    if asks_backlog_policy and is_policy_question:
        if max_backlogs == 0:
            return (
                f"No. {company} requires students "
                "to have no active backlogs."
            )

        return (
            f"{company} allows up to one active "
            "backlog. Students must also have a "
            "CGPA above 8.0."
        )

    # Detect a CGPA supplied in an eligibility question.
    cgpa_match = re.search(
        r"(?:cgpa\s*(?:of|is|=|:)?\s*|"
        r"\b)(\d{1,2}(?:\.\d+)?)\s*"
        r"(?:cgpa\b)?",
        question_lower
    )

    # Avoid interpreting unrelated numbers as CGPA.
    cgpa = None

    explicit_cgpa = re.search(
        r"cgpa\s*(?:of|is|=|:)?\s*(\d{1,2}(?:\.\d+)?)"
        r"|(\d{1,2}(?:\.\d+)?)\s*cgpa",
        question_lower
    )

    if explicit_cgpa:
        cgpa = float(
            explicit_cgpa.group(1)
            or explicit_cgpa.group(2)
        )

    # Detect an explicitly stated backlog count.
    backlog_count = None

    if re.search(r"\bno active backlogs?\b", question_lower):
        backlog_count = 0
    elif re.search(r"\bzero active backlogs?\b", question_lower):
        backlog_count = 0
    elif re.search(
        r"\b(one|1) active backlogs?\b", question_lower
    ):
        backlog_count = 1
    elif re.search(
        r"\b(two|2) active backlogs?\b", question_lower
    ):
        backlog_count = 2

    asks_overall_eligibility = any(
        word in question_lower
        for word in ["eligible", "apply", "qualify"]
    )

    if asks_overall_eligibility:
        if cgpa is not None and cgpa <= required_cgpa:
            return (
                f"No. {company} requires a CGPA above "
                f"{required_cgpa:.1f}; a CGPA of {cgpa:g} "
                "does not meet that requirement."
            )

        if backlog_count is not None and backlog_count > max_backlogs:
            return (
                f"No. {company} allows at most "
                f"{max_backlogs} active backlog(s)."
                if max_backlogs > 0
                else f"No. {company} requires students "
                     "to have no active backlogs."
            )

        if cgpa is not None and backlog_count is not None:
            return (
                f"Yes. The stated CGPA and backlog count "
                f"meet {company}'s listed requirements."
            )

        if cgpa is not None:
            return (
                f"The CGPA meets {company}'s requirement, "
                f"but the student must also have no more "
                f"than {max_backlogs} active backlog(s). "
                "The complete eligibility cannot be "
                "confirmed without the backlog count."
            )

        if backlog_count is not None:
            if backlog_count <= max_backlogs:
                return (
                    f"The backlog count meets {company}'s "
                    f"rule, but the student must also have "
                    f"a CGPA above {required_cgpa:.1f}."
                )

            return (
                f"No. The student exceeds {company}'s "
                "allowed number of active backlogs."
            )

    return None


# --------------------------------------------------
# 7. Ask questions continuously
# --------------------------------------------------

while True:
    question = input(
        "\nAsk a placement question (or type 'exit'): "
    ).strip()

    if question.lower() == "exit":
        print("Exiting RAG application.")
        break

    if not question:
        continue

    # 8. Try deterministic eligibility rules first.
    # These rules avoid LLM contradictions for
    # supported CGPA/backlog questions.

    rule_answer = answer_eligibility_question(question)

    if rule_answer is not None:
        print("\nRAG answer:")
        print(rule_answer)
        print("Answer method: Eligibility rules")
        continue

    # --------------------------------------------------
    # 9. Create question embedding
    # --------------------------------------------------

    start = perf_counter()

    query_vector = embedding_model.encode(
        [question]
    )[0].tolist()

    print(
        f"Question embedding: "
        f"{perf_counter() - start:.2f} seconds"
    )


    # --------------------------------------------------
    # 10. Retrieve relevant chunks
    # --------------------------------------------------

    start = perf_counter()

    TOP_K = 3

    
# Identify the company mentioned in the question
    company = detect_company(question)

    retrieved_chunks = retrieve_chunks(
        question,
        company=company
    )

    if not retrieved_chunks:
        print("\nRAG answer:")
        print("I don't have enough information to answer that.")

    else:
        context = "\n\n".join(
            chunk["text"]
            for chunk in retrieved_chunks
        )

        answer = generate_answer(question, context)

        if answer is None:
            print("\nCould not generate an answer with Ollama.")
        else:
            print("\nRAG answer:")
            print(answer)

    # --------------------------------------------------
    # 11. Prepare the prompt for general questions
    # --------------------------------------------------

    prompt = f"""
You are a college placement assistant.

Answer the question using only the provided context.

Rules:
1. Read the context carefully.
2. If the context answers the question, give that answer.
3. Do not contradict the context.
4. Do not invent facts or requirements.
5. If the answer is not available in the context,
   say exactly:
   "I don't have enough information to answer that."
6. Give a concise, direct answer.

Context:
{context}

Question:
{question}

Answer:
"""


    # --------------------------------------------------
    # 12. Generate the answer using Ollama
    # --------------------------------------------------

    
    answer = generate_answer(question, context)

    if answer is None:
        print("\nCould not generate an answer with Ollama.")
    else:
        print("\nRAG answer:")
        print(answer)
