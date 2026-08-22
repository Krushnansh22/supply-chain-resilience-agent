"""
backend/seed_data/broken_data.py
Owner: Developer 2 (Backend / Simulation)

Contains inconsistent or erroneous data for testing error handling and monitoring.
"""

from pymongo.database import Database

def inject_broken_data(db: Database) -> None:
    """Injects broken/inconsistent data into the database."""
    inventory_collection = db["inventory"]
    
    # Inconsistent data: negative stock
    inventory_collection.update_one(
        {"component_id": "BROKEN-001"},
        {"$set": {
            "component_id": "BROKEN-001",
            "current_stock": -50,
            "usable_stock": -50,
            "daily_usage": 10.0,
            "safety_stock": 100
        }},
        upsert=True
    )
    print("Broken data injected for testing.")
