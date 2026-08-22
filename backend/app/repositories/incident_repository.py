from pymongo.database import Database
from app.repositories.base_repository import BaseRepository

class IncidentRepository(BaseRepository):
    def __init__(self, db: Database):
        super().__init__(db, "incidents")

    def get_by_incident_id(self, incident_id: str):
        return self.get_by_field("incident_id", incident_id)

    def list_all_ordered(self, field: str, direction: int):
        return list(self.collection.find({}, {"_id": 0}).sort(field, direction))
