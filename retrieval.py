
import chromadb
from document_router import detect_source

from sentence_transformers import SentenceTransformer

from config import (
    CHROMA_DB_PATH,
    COLLECTION_NAME,
    EMBEDDING_MODEL,
    TOP_K,
)

# Load the embedding model
embedding_model = SentenceTransformer(EMBEDDING_MODEL)

# Connect to the persistent ChromaDB database
db_client = chromadb.PersistentClient(
    path=str(CHROMA_DB_PATH)
)

# Access the existing collection
collection = db_client.get_collection(
    name=COLLECTION_NAME
)


def retrieve_chunks(question, company=None, source=None):
    """Retrieve relevant document chunks for a question."""

    if collection.count() == 0:
        return []

    # Convert the question into an embedding
    question_embedding = embedding_model.encode(
        question
    ).tolist()

    # Build the search arguments
    search_args = {
        "query_embeddings": [question_embedding],
        "n_results": min(TOP_K, collection.count()),
        "include": [
            "documents",
            "metadatas",
            "distances",
        ],
    }

    # Filter results when a source is specified
    if source:
        search_args["where"] = {
            "source": source
        }

    # Search ChromaDB
    results = collection.query(**search_args)

    documents = results["documents"][0]
    metadatas = results["metadatas"][0]
    distances = results["distances"][0]

    retrieved_chunks = []

    for document, metadata, distance in zip(
        documents, metadatas, distances
    ):
        retrieved_chunks.append({
            "text": document,
            "metadata": metadata or {},
            "distance": distance,
        })

    return retrieved_chunks
