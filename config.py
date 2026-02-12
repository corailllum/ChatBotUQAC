"""
Configuration pour l'agent RAG UQAC
"""
from pathlib import Path


BASE_URL = "https://www.uqac.ca/mgestion/" # URL de base du manuel de gestion
MAX_PAGES = 250  # Limite pour ne pas surcharger le serveur

CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200  # Chevauchement entre les morceaux

PROJECT_ROOT = Path(__file__).parent
PERSIST_DIRECTORY = PROJECT_ROOT / "data2" / "chromadb"  # TODO : à modifier au besoin
PERSIST_DIRECTORY.mkdir(parents=True, exist_ok=True)

# Options: nomic-embed-text, mxbai-embed-large, snowflake-arctic-embed
EMBEDDING_MODEL = "nomic-embed-text"

LLM_MODEL = "llama3.2"