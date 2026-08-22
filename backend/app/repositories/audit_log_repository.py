from pymongo.database import Database
from app.repositories.base_repository import BaseRepository

class AuditLogRepository(BaseRepository):
    def __init__(self, db: Database):
        super().__init__(db, "audit_logs")

    # AuditLog model has 'id' (int), 'incident_id' (str), etc.
    def get_by_incident_id(self, incident_id: str) -> list[dict]:
        return list(self.collection.find({"incident_id": incident_id}, {"_id": 0}))
