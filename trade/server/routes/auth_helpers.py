"""
Helper endpoint for NextAuth integration
Saves user data from NextAuth to backend database
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from typing import Optional
import logging
from datetime import datetime
from services.database import get_db_connection

router = APIRouter()
log = logging.getLogger(__name__)

class SaveUserRequest(BaseModel):
    id: str
    email: EmailStr
    name: Optional[str] = None
    picture: Optional[str] = None

@router.post("/save-user")
async def save_user(request: SaveUserRequest):
    """
    Save or update user from NextAuth
    Called by NextAuth signIn callback
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if user exists
        existing_user = cursor.execute(
            "SELECT * FROM users WHERE email = ?", (request.email,)
        ).fetchone()
        
        if existing_user:
            # Update existing user
            cursor.execute(
                """UPDATE users 
                   SET name = ?, picture = ?, last_login = ? 
                   WHERE email = ?""",
                (request.name, request.picture, datetime.utcnow(), request.email)
            )
            log.info(f"Updated user: {request.email}")
        else:
            # Create new user with 100 free credits
            cursor.execute(
                """INSERT INTO users (email, name, picture, credits_balance, subscription_tier, email_verified) 
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (request.email, request.name, request.picture, 100, "free", True)
            )
            log.info(f"New user created with 100 free credits: {request.email}")
        
        conn.commit()
        conn.close()
        
        return {"success": True, "message": "User saved successfully"}
        
    except Exception as e:
        log.error(f"Error saving user: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to save user: {str(e)}")

@router.get("/user/{email}")
async def get_user(email: str):
    """Get user data by email"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        user = cursor.execute(
            "SELECT * FROM users WHERE email = ?", (email,)
        ).fetchone()
        
        conn.close()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        return {
            "id": user["id"],
            "email": user["email"],
            "name": user["name"],
            "picture": user["picture"],
            "credits": user["credits_balance"],
            "subscription_tier": user["subscription_tier"],
            "created_at": user["created_at"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Error getting user: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get user: {str(e)}")
