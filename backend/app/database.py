"""
app/database.py
Owner: Developer 2 (Backend / Simulation)

SQLAlchemy engine + session factory + declarative Base, and the FastAPI dependency
`get_db()` that every route/tool uses to talk to SQLite.

RECEIVES: DATABASE_URL from config.settings
DELIVERS:
  - `Base`     -> imported by every file in app/models/ to define ORM tables
  - `get_db()` -> imported by every file in app/api/ and app/tools/ as a FastAPI Depends()
  - `init_db()`-> called once at startup (see main.py) to create tables + call seed_data
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from app.config import settings

# Ensure the data/ directory exists before SQLite tries to open the file (BUG FIX)
if settings.DATABASE_URL.startswith("sqlite"):
    db_path = settings.DATABASE_URL.replace("sqlite:///", "")
    db_dir = os.path.dirname(db_path)
    if db_dir:
        os.makedirs(db_dir, exist_ok=True)

# check_same_thread=False is needed because SQLite + FastAPI's threaded workers
connect_args = {"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(settings.DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """FastAPI dependency. Yields a DB session per-request and closes it after."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Create all tables (from app/models/*) and load hero-scenario seed data.
    Called once from main.py on app startup.

    TODO (Dev2): import app.simulator.seed_data and call its `run()` here after
    Base.metadata.create_all so the demo DB always starts in the same known state.
    """
    # Importing models here (not at module top) avoids circular imports, since
    # models import `Base` from this file.
    from app.models import (  # noqa: F401
        inventory,
        suppliers,
        purchase_orders,
        production_orders,
        rfqs,
        supplier_messages,
        incidents,
        audit_logs,
    )

    Base.metadata.create_all(bind=engine)

    # Seed hero scenario (COMP-104 -> PO-7712 -> SUP-21 -> PROD-882) on first run
    from app.simulator.seed_data import run as seed_run
    db = SessionLocal()
    try:
        seed_run(db)
    finally:
        db.close()
