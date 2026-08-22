"""
app/mongo_database.py
Owner: Developer 2 (Backend / Simulation)

MongoDB connection setup using PyMongo.
"""

from pymongo import MongoClient
from app.config import settings

client = MongoClient(settings.MONGO_URI or "mongodb://127.0.0.1:27017", serverSelectionTimeoutMS=10000)
db = client[settings.MONGO_DB_NAME]

def get_mongo_db():
    """FastAPI dependency."""
    return db


def ping_mongo() -> None:
    if not settings.MONGO_URI:
        raise RuntimeError("MONGO_URI must be configured with the MongoDB Atlas connection string")
    client.admin.command("ping")
