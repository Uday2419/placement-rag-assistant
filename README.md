
# Placement RAG Assistant

A Retrieval-Augmented Generation (RAG) application that answers placement-related questions using a college placement knowledge base.

## Features

- Retrieves relevant information from placement documents.
- Generates answers using an Ollama language model.
- Uses Sentence Transformers for text embeddings.
- Stores and searches embeddings using ChromaDB.
- Supports conversational follow-up questions using chat history.
- Handles placement eligibility questions using predefined rules.
- Provides an API using FastAPI.
- Supports Docker-based execution.
- Includes automated tests.

## Tech Stack

- Python
- FastAPI
- Ollama
- Sentence Transformers
- ChromaDB
- Docker
- Git and GitHub

## How It Works

1. Placement documents are loaded and processed.
2. Documents are converted into vector embeddings.
3. Embeddings are stored in ChromaDB.
4. A user submits a question.
5. The application retrieves relevant document chunks.
6. Retrieved context is passed to the Ollama language model.
7. The model generates an answer using the retrieved context.

Placement eligibility questions are handled separately using predefined eligibility rules.

## Project Structure

```text
basic-rag/
|-- api.py
|-- main.py
|-- config.py
|-- retrieval.py
|-- generation.py
|-- contextualizer.py
|-- document_loader.py
|-- document_router.py
|-- test_api.py
|-- test_contextualizer.py
|-- test_eligibility.py
|-- requirements.txt
|-- Dockerfile
|-- docker-compose.yml
|-- .dockerignore
|-- .gitignore
`-- README.md

## Local Setup

Clone the repository:

```bash
git clone https://github.com/Uday2419/placement-rag-assistant.git
cd placement-rag-assistant
```

Create a virtual environment:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
pip install -r requirements.txt
```

Make sure Ollama is installed and running. Pull the configured model if necessary:

```powershell
ollama pull llama3.2:3b
```

Start the API:

```powershell
python -m uvicorn api:app --reload --port 8001
```

## API Documentation

Once the application is running, open:

http://127.0.0.1:8001/docs

Main endpoint:

`POST /ask`

The endpoint accepts a question and optional conversation history.

## Running Tests

Run the automated tests:

```powershell
python -m unittest test_eligibility test_contextualizer test_api -v
```


## Docker Setup

### Prerequisites

- Docker Desktop must be installed and running.
- Ollama must be running on the host machine.
- The configured Ollama model must be available locally.

### Start the Application

Run from the project directory:

```powershell
docker compose up --build
```

The API will be available at:

http://localhost:8002

Swagger UI documentation:

http://localhost:8002/docs

### Stop the Application

```powershell
docker compose down
```

Note: Stopping the Docker container does not stop Ollama running on the host machine.

## Future Improvements

- Improve retrieval relevance and answer quality.
- Add more placement documents.
- Implement retrieval evaluation metrics.
- Improve conversational contextualization.
- Deploy the application to a cloud platform.
- Add authentication and persistent conversation storage.

## Author

**Uday Ramesh Dherange**

GitHub: [Uday2419](https://github.com/Uday2419)
