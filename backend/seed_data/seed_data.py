"""
backend/seed_data/seed_data.py
Owner: Developer 2 (Backend / Simulation)

Populates MongoDB with hero scenario data + filler data using the new Repository layer.
"""

from datetime import datetime, timedelta
from pymongo.database import Database
from app.repositories.inventory_repository import InventoryRepository

def run(db: Database) -> None:
    """Seeds the MongoDB with the hero scenario and additional filler data."""
    inventory_repo = InventoryRepository(db)
    supplier_collection = db["suppliers"]
    po_collection = db["purchase_orders"]
    prod_collection = db["production_orders"]
    
    # Check if already seeded
    if inventory_repo.collection.count_documents({}) > 0:
        return

    # 1. Seed Inventory
    inventory_data = [
        {"component_id": "COMP-104", "current_stock": 390, "usable_stock": 390, "daily_usage": 90.0, "safety_stock": 100},
        {"component_id": "COMP-105", "current_stock": 500, "usable_stock": 500, "daily_usage": 50.0, "safety_stock": 150},
        {"component_id": "COMP-201", "current_stock": 100, "usable_stock": 80, "daily_usage": 20.0, "safety_stock": 50},
    ]
    for item in inventory_data:
        inventory_repo.update({"component_id": item["component_id"]}, item)

    # 2. Seed Suppliers
    suppliers = [
        {"supplier_id": "SUP-21", "name": "Alpha Components Pvt Ltd", "quality_score": 88, "reliability_score": 72, "certifications": "ISO9001"},
        {"supplier_id": "SUP-18", "name": "Beta Precision Supplies", "quality_score": 95, "reliability_score": 91, "certifications": "ISO9001,RoHS"},
        {"supplier_id": "SUP-42", "name": "Gamma Rapid Parts", "quality_score": 80, "reliability_score": 85, "certifications": "RoHS"},
    ]
    for s in suppliers:
        supplier_collection.update_one({"supplier_id": s["supplier_id"]}, {"$set": s}, upsert=True)

    # 3. Seed Purchase Orders
    pos = [
        {"po_id": "PO-7712", "component_id": "COMP-104", "supplier_id": "SUP-21", "quantity": 600, "status": "DELAYED", "unit_price": 140.0},
        {"po_id": "PO-8813", "component_id": "COMP-201", "supplier_id": "SUP-42", "quantity": 300, "status": "OPEN", "unit_price": 45.0},
    ]
    for po in pos:
        po_collection.update_one({"po_id": po["po_id"]}, {"$set": po}, upsert=True)

    # 4. Seed Production Orders
    prods = [
        {"production_id": "PROD-882", "product": "Widget-X", "component_id": "COMP-104", "quantity": 200, "component_per_unit": 3, "deadline": datetime.utcnow() + timedelta(days=6), "priority": "HIGH", "status": "ON_TRACK"},
        {"production_id": "PROD-990", "product": "Widget-Y", "component_id": "COMP-201", "quantity": 50, "component_per_unit": 1, "deadline": datetime.utcnow() + timedelta(days=12), "priority": "MEDIUM", "status": "ON_TRACK"},
    ]
    for p in prods:
        prod_collection.update_one({"production_id": p["production_id"]}, {"$set": p}, upsert=True)

    print("Database seeded with comprehensive data successfully.")
