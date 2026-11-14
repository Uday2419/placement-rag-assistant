
import os
from time import perf_counter

import ollama

from config import LLM_MODEL


# Connect to local Ollama or a custom Ollama server.
OLLAMA_HOST = os.getenv(
    "OLLAMA_HOST",
    "http://localhost:11434"
)

ollama_client = ollama.Client(host=OLLAMA_HOST)


def generate_answer(question, context):

    prompt = f"""
You are a helpful college placement assistant.

Answer using only the provided context.

Follow these rules:
1. Never invent facts or eligibility requirements.
2. If the context contains a direct answer, answer it clearly.
3. If the context contains related general information but
   not company-specific information, share that information
   and clearly explain that it is general college information.
4. Never present general placement-cell activities as
   activities conducted by a specific company.
5. If neither direct nor relevant related information exists,
   say: "I don't have enough information to answer that."

Context:
{context}

Question:
{question}

Answer:
"""

    try:
        start = perf_counter()

        response = ollama_client.chat(
            model=LLM_MODEL,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            options={
                "num_predict": 100,
                "temperature": 0
            }
        )

        print(
            f"Ollama generation: "
            f"{perf_counter() - start:.2f} seconds"
        )

        return response["message"]["content"].strip()

    except Exception as error:
        print("\nCould not generate an answer with Ollama.")
        print("Error:", error)
        return None
