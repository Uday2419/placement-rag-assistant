
from time import perf_counter
import ollama

from config import LLM_MODEL


def generate_answer(question, context):
    prompt = f"""
You are a helpful college placement assistant.

Answer using only the provided context.
Do not invent facts or eligibility requirements.
If the context does not contain the answer, say:
"I don't have enough information to answer that."

Context:
{context}

Question:
{question}

Answer:
"""

    try:
        start = perf_counter()

        response = ollama.chat(
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
