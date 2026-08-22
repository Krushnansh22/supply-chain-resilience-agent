from pymongo.database import Database
from app.repositories.base_repository import BaseRepository

class ProductionOrderRepository(BaseRepository):
    def __init__(self, db: Database):
        super().__init__(db, "production_orders")

    def get_by_production_id(self, production_id: str):
        return self.get_by_field("production_id", production_id)
