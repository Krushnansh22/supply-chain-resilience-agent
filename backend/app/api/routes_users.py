"""
app/api/routes_users.py
API endpoints for RBAC user profiles and warehouse registries.
"""

from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Request
from pymongo.database import Database

from app.mongo_database import get_mongo_db
from app.middleware.rbac import get_current_user_and_scope

router = APIRouter(prefix="/users", tags=["Users & RBAC"])


@router.get("/me")
def get_current_user_profile(
    context: Dict[str, Any] = Depends(get_current_user_and_scope)
) -> Dict[str, Any]:
    """Returns the authenticated user's profile and active warehouse scope."""
    return {
        "user": context["user"],
        "role": context["role"],
        "assigned_warehouse": context["assigned_warehouse"],
        "effective_warehouse": context["effective_warehouse"],
    }


@router.get("", response_model=List[Dict[str, Any]])
def list_users(db: Database = Depends(get_mongo_db)) -> List[Dict[str, Any]]:
    """Lists available users for role switching / user management."""
    users = list(db["users"].find({}, {"_id": 0}))
    return users


@router.get("/warehouses/all")
def list_warehouses(db: Database = Depends(get_mongo_db)) -> List[Dict[str, Any]]:
    """Lists all operational warehouses in the supply chain network."""
    warehouses = list(db["warehouses"].find({}, {"_id": 0}))
    return warehouses
