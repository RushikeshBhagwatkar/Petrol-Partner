from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from pydantic import BaseModel

router = APIRouter(prefix="/admin", tags=["admin"])

# Mock Admin Credentials from prompt
ADMIN_EMAIL = "adminpetrolpartner@gmail.com"
ADMIN_PASSWORD = "Admin@1234"

class AdminLogin(BaseModel):
    email: str
    password: str

@router.post("/login")
async def admin_login(payload: AdminLogin):
    if payload.email == ADMIN_EMAIL and payload.password == ADMIN_PASSWORD:
        return {"status": "success", "token": "mock-admin-jwt-token", "role": "super_admin"}
    raise HTTPException(status_code=401, detail="Invalid admin credentials")

@router.get("/stats")
async def get_global_stats():
    # In production, this would query the analytics-service or the main DB
    return {
        "daily_active_users": 1250,
        "active_rides": 45,
        "completed_rides_today": 89,
        "revenue_total": 45000.50,
        "safety_alerts": 0
    }

@router.get("/users")
async def list_all_users():
    return [{"uid": "user1", "name": "Rajesh Kumar", "trust_score": 85, "status": "active"}]

@router.post("/users/{uid}/suspend")
async def suspend_user(uid: str):
    return {"status": "success", "message": f"User {uid} suspended"}
