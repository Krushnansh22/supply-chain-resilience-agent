"""
app/mongo_database.py
Owner: Developer 2 (Backend / Simulation)

MongoDB connection setup using PyMongo.
"""

from pymongo import MongoClient
from app.config import settings

# Initialize PyMongo client
client = MongoClient(settings.MONGO_URI)
db = client["supply_chain_db"]

def get_mongo_db():
    """FastAPI dependency."""
    return db
