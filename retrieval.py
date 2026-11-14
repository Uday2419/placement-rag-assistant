
import chromadb

from functools import lru_cache
from sentence_transformers import SentenceTransformer

from config import (
    CHROMA_DB_PATH,
    COLLECTION_NAME,
    EMBEDDING_MODEL,
    TOP_K,
)


# --------------------------------------------------
# 1. Load resources only when retrieval is requested
# --------------------------------------------------

@lru_cache(maxsize=1)
def load_resources():

    print("Loading embedding model...")

    embedding_model = SentenceTransformer(EMBEDDING_MODEL)

    print("Connecting to ChromaDB...")

    db_client = chromadb.PersistentClient(
        path=str(CHROMA_DB_PATH)
    )

    try:
        collection = db_client.get_collection(
            name=COLLECTION_NAME
        )

    except Exception as error:
        raise RuntimeError(
            f"ChromaDB collection '{COLLECTION_NAME}' "
            "was not found. Run index_documents.py first."
        ) from error

    print("Retrieval resources loaded successfully.")

    return embedding_model, db_client, collection


# --------------------------------------------------
# 2. Retrieve relevant document chunks
# --------------------------------------------------

def retrieve_chunks(question, company=None, source=None):

    """
    Retrieve relevant document chunks using similarity search.

    company is retained for compatibility, but company-based
    filtering is not enabled until company metadata is indexed.
    """

    if not question or not question.strip():
        return []

    embedding_model, db_client, collection = load_resources()

    total_records = collection.count()

    if total_records == 0:
        return []

    # Convert question into an embedding.
    question_embedding = embedding_model.encode(
        question
    ).tolist()

    # Build ChromaDB search arguments.
    search_args = {
        "query_embeddings": [question_embedding],
        "n_results": min(TOP_K, total_records),
        "include": [
            "documents",
            "metadatas",
            "distances",
        ],
    }

    # Apply source filtering when requested.
    if source:
        search_args["where"] = {
            "source": source
        }

    # Perform similarity search.
    results = collection.query(**search_args)

    documents = results["documents"][0] or []
    metadatas = results["metadatas"][0] or []
    distances = results["distances"][0] or []

    retrieved_chunks = []

    for document, metadata, distance in zip(
        documents,
        metadatas,
        distances
    ):

        if not document:
            continue

        retrieved_chunks.append({
            "text": document,
            "metadata": metadata or {},
            "distance": distance,
        })

    return retrieved_chunks
