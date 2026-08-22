"""Backward-compatible database imports delegated to MongoDB Atlas."""

from sqlalchemy.orm import declarative_base
from app.mongo_database import get_mongo_db

Base = declarative_base()


def get_db():
    """Legacy dependency name retained for callers while returning MongoDB."""
    yield get_mongo_db()


def init_db():
    """Legacy no-op; MongoDB is initialized by app.main startup."""
    return None
