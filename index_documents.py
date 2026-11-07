from document_loader import load_documents
from retrieval import embedding_model, collection


def index_documents():

    documents = load_documents()

    all_chunks = []
    all_ids = []
    all_metadatas = []

    for document_number, document in enumerate(documents):

        text = document["text"]
        source = document["source"]

        chunks = text.split("\n\n")

        for chunk_number, chunk in enumerate(chunks):

            if not chunk.strip():
                continue

            chunk_id = f"{source}_{chunk_number}"

            metadata = {
                "source": source,
                "chunk_number": chunk_number
            }

            all_chunks.append(chunk)
            all_ids.append(chunk_id)
            all_metadatas.append(metadata)

    if all_chunks:

        embeddings = embedding_model.encode(
            all_chunks
        ).tolist()

        collection.upsert(
            ids=all_ids,
            documents=all_chunks,
            embeddings=embeddings,
            metadatas=all_metadatas
        )

    print("Total documents loaded:", len(documents))
    print("Total chunks indexed:", len(all_chunks))
    print("Total chunks in ChromaDB:", collection.count())


if __name__ == "__main__":
    index_documents()