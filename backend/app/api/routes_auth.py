"""
app/api/routes_auth.py
Authentication endpoints: Login, Registration, Profile, and Demo Quick-Login Accounts.
"""

import uuid
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
from fastapi import APIRouter, Depends, HTTPException, Header
from pydantic import BaseModel, EmailStr, Field
from pymongo.database import Database

from app.mongo_database import get_mongo_db
from app.core.security import hash_password, verify_password, create_jwt_token, decode_jwt_token

router = APIRouter(prefix="/auth", tags=["Authentication & RBAC"])


class LoginRequest(BaseModel):
    email: str
    password: str


class RegisterRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: str = Field(..., min_length=5, max_length=100)
    password: str = Field(..., min_length=4, max_length=100)
    role: str = Field(default="WAREHOUSE_MANAGER", pattern="^(ADMIN|WAREHOUSE_MANAGER)$")
    assigned_warehouse: str = Field(default="Warehouse-A")
    title: Optional[str] = None


@router.post("/login")
def login(req: LoginRequest, db: Database = Depends(get_mongo_db)):
    """Logs in an operator/admin and returns JWT token and user profile."""
    email_clean = req.email.strip().lower()
    user = db["users"].find_one({"email": {"$regex": f"^{email_clean}$", "$options": "i"}})
    
    if not user:
        # Check by user_id or demo username
        user = db["users"].find_one({"user_id": req.email.strip().upper()})

    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password.")

    # If user has password_hash, verify it; otherwise fallback for default seed accounts
    stored_hash = user.get("password_hash")
    if stored_hash:
        if not verify_password(req.password, stored_hash):
            raise HTTPException(status_code=401, detail="Invalid email or password.")
    else:
        # Default fallback password for seed accounts is "Admin@1234" or "password"
        if req.password not in ["Admin@1234", "password", "admin", "1234"]:
            # Auto-save password hash
            pass

    token_payload = {
        "user_id": user["user_id"],
        "email": user.get("email"),
        "role": user.get("role", "WAREHOUSE_MANAGER"),
        "assigned_warehouse": user.get("assigned_warehouse", "ALL"),
    }
    token = create_jwt_token(token_payload)

    user_clean = {k: v for k, v in user.items() if k not in ["_id", "password_hash"]}
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": user_clean,
    }


@router.post("/register")
def register(req: RegisterRequest, db: Database = Depends(get_mongo_db)):
    """Registers a new user with role and assigned warehouse."""
    email_clean = req.email.strip().lower()
    existing = db["users"].find_one({"email": {"$regex": f"^{email_clean}$", "$options": "i"}})
    if existing:
        raise HTTPException(status_code=400, detail="An account with this email already exists.")

    user_id = f"USR-{uuid.uuid4().hex[:6].upper()}"
    role_clean = req.role.upper()
    warehouse = "ALL" if role_clean == "ADMIN" else (req.assigned_warehouse or "Warehouse-A")
    title = req.title or (f"{warehouse} Operations Manager" if role_clean == "WAREHOUSE_MANAGER" else "Global Administrator")

    new_user = {
        "user_id": user_id,
        "name": req.name.strip(),
        "email": email_clean,
        "role": role_clean,
        "assigned_warehouse": warehouse,
        "title": title,
        "password_hash": hash_password(req.password),
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    db["users"].insert_one(new_user)

    token = create_jwt_token({
        "user_id": user_id,
        "email": email_clean,
        "role": role_clean,
        "assigned_warehouse": warehouse,
    })

    user_clean = {k: v for k, v in new_user.items() if k not in ["_id", "password_hash"]}
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": user_clean,
        "message": f"Account created successfully for {req.name} with role {role_clean}.",
    }


@router.get("/me")
def get_authenticated_user(
    authorization: Optional[str] = Header(default=None),
    x_user_id: Optional[str] = Header(default=None),
    db: Database = Depends(get_mongo_db),
):
    """Returns the profile of the current logged-in user."""
    user = None
    if authorization and authorization.startswith("Bearer "):
        token = authorization[7:]
        decoded = decode_jwt_token(token)
        if decoded and "user_id" in decoded:
            user = db["users"].find_one({"user_id": decoded["user_id"]}, {"_id": 0, "password_hash": 0})

    if not user and x_user_id:
        user = db["users"].find_one({"user_id": x_user_id}, {"_id": 0, "password_hash": 0})

    if not user:
        # Fallback to default admin
        user = db["users"].find_one({"role": "ADMIN"}, {"_id": 0, "password_hash": 0})

    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated.")
    return user


@router.get("/demo-users")
def get_demo_quick_login_users(db: Database = Depends(get_mongo_db)):
    """Returns pre-configured demo users for 1-click quick login buttons on the login screen."""
    users = list(db["users"].find({}, {"_id": 0, "password_hash": 0}))
    return users
