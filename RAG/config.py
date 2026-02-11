"""
Configuration pour l'agent RAG UQAC
"""

BASE_URL = "https://www.uqac.ca/mgestion/" # URL de base du manuel de gestion
MAX_PAGES = 50  # Limite pour ne pas surcharger le serveur

CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200  # Chevauchement entre les morceaux

PERSIST_DIRECTORY = "./data/chroma_db"  # Où sauvegarder la base de données

# Options: nomic-embed-text, mxbai-embed-large, snowflake-arctic-embed
EMBEDDING_MODEL = "nomic-embed-text"

LLM_MODEL = "llama3.2"