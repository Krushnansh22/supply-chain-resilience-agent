"""
app/api/routes_production.py
Owner: Developer 2 (Backend / Simulation)
"""

from fastapi import APIRouter, Depends, HTTPException
from pymongo.database import Database

from app.mongo_database import get_mongo_db
from app.repositories.production_order_repository import ProductionOrderRepository
from app.schemas.common import ProductionOrderOut

router = APIRouter()

def get_repo(db: Database = Depends(get_mongo_db)):
    return ProductionOrderRepository(db)


@router.get("/", response_model=list[ProductionOrderOut])
def list_production_orders(repo: ProductionOrderRepository = Depends(get_repo)):
    return repo.list_all()


@router.get("/{production_id}", response_model=ProductionOrderOut)
def get_production_order(production_id: str, repo: ProductionOrderRepository = Depends(get_repo)):
    row = repo.get_by_production_id(production_id)
    if not row:
        raise HTTPException(status_code=404, detail="production order not found")
    return row

# TODO (Dev3): expose a /production/{id}/risk endpoint wrapping decision_engine/production_risk.py
