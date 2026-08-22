from pymongo.database import Database
from datetime import datetime
from app.repositories.base_repository import BaseRepository

class AuditLogRepository(BaseRepository):
    def __init__(self, db: Database):
        super().__init__(db, "audit_logs")

    # AuditLog model has 'id' (int), 'incident_id' (str), etc.
    def get_by_incident_id(self, incident_id: str) -> list[dict]:
        return self._clean(list(self.collection.find({"incident_id": incident_id}, {"_id": 0})))

    def list_all(self) -> list[dict]:
        return self._clean(list(self.collection.find({}, {"_id": 0}).sort("timestamp", 1)))

    @staticmethod
    def _clean(rows: list[dict]) -> list[dict]:
        fallback = datetime.utcnow()
        for row in rows:
            row.setdefault("timestamp", fallback)
        return rows
