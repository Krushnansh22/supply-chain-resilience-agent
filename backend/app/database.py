"""Backward-compatible database imports delegated to MongoDB Atlas."""

from sqlalchemy.orm import declarative_base
from app.mongo_database import get_mongo_db

Base = declarative_base()


class SessionLocal:
    """Mock SQL session class delegating to PyMongo Database for verify_all.py."""
    def __init__(self):
        self.db = get_mongo_db()
        
    def __getitem__(self, name):
        return self.db[name]
        
    def close(self):
        pass


def get_db():
    """Legacy dependency name retained for callers while returning MongoDB."""
    yield get_mongo_db()


def init_db():
    """Legacy no-op; MongoDB is initialized by app.main startup."""
    return None
