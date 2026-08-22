"""
app/repositories/base_repository.py
Owner: Developer 2 (Backend / Simulation)

Base class for repositories to handle common MongoDB operations.
"""

from pymongo.database import Database

class BaseRepository:
    def __init__(self, db: Database, collection_name: str):
        self.collection = db[collection_name]

    def list_all(self) -> list[dict]:
        # Remove _id from results to keep it clean
        return list(self.collection.find({}, {"_id": 0}))

    def get_by_field(self, field_name: str, value: str) -> dict:
        return self.collection.find_one({field_name: value}, {"_id": 0})

    def insert(self, data: dict):
        self.collection.insert_one(data)

    def update(self, filter_query: dict, update_data: dict):
        self.collection.update_one(filter_query, {"$set": update_data}, upsert=True)
