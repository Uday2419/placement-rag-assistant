
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Literal

from main import answer_eligibility_question, detect_company
from retrieval import retrieve_chunks
from generation import generate_answer
from contextualizer import contextualize_question


app = FastAPI(
    title="Placement RAG Assistant",
    description="API for a Placement Question Answering System",
    version="1.2"
)


class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class QuestionRequest(BaseModel):
    question: str
    chat_history: list[ChatMessage] = Field(default_factory=list)


@app.get("/")
def home():
    return {
        "message": "Placement RAG API is running!"
    }


@app.post("/ask")
def ask_question(request: QuestionRequest):

    question = request.question.strip()

    if not question:
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty."
        )

    chat_history = [
        message.model_dump()
        for message in request.chat_history
    ]

    contextualized_question = contextualize_question(
        question,
        chat_history
    )

    rule_answer = answer_eligibility_question(
        contextualized_question
    )

    if rule_answer is not None:
        return {
            "question": question,
            "contextualized_question": contextualized_question,
            "answer": rule_answer,
            "answer_method": "Eligibility rules",
            "sources": []
        }

    company = detect_company(contextualized_question)

    # Step 1: Retrieve relevant chunks.
    try:
        retrieved_chunks = retrieve_chunks(
            contextualized_question,
            company=company
        )

        # Step 2: Expand retrieval for workshop questions.
        if "workshop" in contextualized_question.lower():

            general_chunks = retrieve_chunks(
                "What workshops does the placement cell conduct?"
            )

            combined_chunks = []
            seen_chunks = set()

            for chunk in retrieved_chunks + general_chunks:

                key = (
                    chunk["metadata"].get("source"),
                    chunk["text"]
                )

                if key not in seen_chunks:
                    seen_chunks.add(key)
                    combined_chunks.append(chunk)

            retrieved_chunks = combined_chunks

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Retrieval failed: {str(error)}"
        )

    if not retrieved_chunks:
        return {
            "question": question,
            "contextualized_question": contextualized_question,
            "answer": "I don't have enough information to answer that.",
            "answer_method": "RAG",
            "sources": []
        }

    # Step 3: Prepare context and sources.
    context_parts = []
    sources = set()

    for chunk in retrieved_chunks:

        source = chunk["metadata"].get(
            "source", "Unknown"
        )

        context_parts.append(
            f"Source: {source}\nInformation: {chunk['text']}"
        )

        sources.add(source)

    context = "\n\n".join(context_parts)

    # Step 4: Generate answer.
    try:
        generation_question = contextualized_question

        if "workshop" in contextualized_question.lower():
            generation_question = (
                f"According to the provided context, "
                f"what workshops does the college placement cell conduct? "
                f"Does the context say that {company} conducts its own workshops? "
                f"Clearly distinguish general college activities from "
                f"company-specific activities. Do not invent information."
            )

        answer = generate_answer(
            generation_question,
            context
        )
    except Exception as error:
        raise HTTPException(
            status_code=503,
            detail=f"Answer generation failed: {str(error)}"
        )

    if answer is None:
        raise HTTPException(
            status_code=503,
            detail="Could not generate an answer. Check whether Ollama is running."
        )

    return {
        "question": question,
        "contextualized_question": contextualized_question,
        "answer": answer,
        "answer_method": "RAG",
        "sources": sorted(sources)
    }
