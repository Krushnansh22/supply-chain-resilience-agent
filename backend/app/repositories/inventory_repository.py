"""
app/repositories/inventory_repository.py
Owner: Developer 2 (Backend / Simulation)

Repository for Inventory data in MongoDB.
"""

from pymongo.database import Database
from app.repositories.base_repository import BaseRepository

class InventoryRepository(BaseRepository):
    def __init__(self, db: Database):
        super().__init__(db, "inventory")

    def get_by_component_id(self, component_id: str):
        return self.get_by_field("component_id", component_id)
