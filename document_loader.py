from pathlib import Path

from config import BASE_DIR

DATA_DIR = BASE_DIR / "data"


def load_documents():

    documents = []

    files = list(DATA_DIR.glob("*.txt"))

    for file in files:

        with open(file, "r", encoding="utf-8") as f:

            text = f.read()

            documents.append({
                "text": text,
                "source": file.name
            })

    return documents