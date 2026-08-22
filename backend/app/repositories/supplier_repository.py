from pymongo.database import Database
from app.repositories.base_repository import BaseRepository

class SupplierRepository(BaseRepository):
    def __init__(self, db: Database):
        super().__init__(db, "suppliers")

    def get_by_supplier_id(self, supplier_id: str):
        return self.get_by_field("supplier_id", supplier_id)
