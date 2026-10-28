
from pathlib import Path

# Project directory
BASE_DIR = Path(__file__).resolve().parent

# Document settings
DATA_FILE = BASE_DIR / "data" / "placement.txt"

# ChromaDB settings
CHROMA_DB_PATH = BASE_DIR / "chroma_db"
COLLECTION_NAME = "placement_knowledge"

# Model settings
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
LLM_MODEL = "llama3.2:3b"

# Retrieval settings
TOP_K = 3

# Index settings
REBUILD_INDEX = False
