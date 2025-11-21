import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

_client = None

def get_db_connection():
    """Retorna objeto MongoClient já conectado.
    Configurar a URI em MONGO_URI no ambiente.
    """
    global _client
    if _client:
        return _client
    mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    _client = MongoClient(mongo_uri)
    return _client
