"""
Direct Google OAuth 2.0 Implementation
No Supabase dependency - full control over authentication
"""
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from typing import Optional
import os
import secrets
import jwt
import httpx
from datetime import datetime, timedelta
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
import logging

router = APIRouter()
log = logging.getLogger(__name__)

# Configuration from environment
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
FRONTEND_URL = os.getenv("NEXT_PUBLIC_APP_URL", "https://tradeberg-frontend-qwx0.onrender.com")
JWT_SECRET = os.getenv("JWT_SECRET", os.getenv("SECRET_KEY"))
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24

# In-memory state storage (use Redis in production)
oauth_states = {}

# ============================================
# MODELS
# ============================================

class GoogleAuthInitRequest(BaseModel):
    redirect_url: Optional[str] = None

class GoogleAuthInitResponse(BaseModel):
    auth_url: str

class GoogleCallbackRequest(BaseModel):
    code: str

class AuthResponse(BaseModel):
    success: bool
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    user: Optional[dict] = None
    message: Optional[str] = None

# ============================================
# HELPER FUNCTIONS
# ============================================

def create_jwt_token(user_data: dict) -> str:
    """Create JWT token for authenticated user"""
    payload = {
        "user_id": user_data["id"],
        "email": user_data["email"],
        "name": user_data.get("name"),
        "exp": datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS),
        "iat": datetime.utcnow()
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

async def get_or_create_user(google_user_data: dict):
    """Get existing user or create new one with 100 credits"""
    from database import SessionLocal
    from models.user import User
    
    db = SessionLocal()
    try:
        # Check if user exists
        user = db.query(User).filter(User.email == google_user_data["email"]).first()
        
        if user:
            # Update last login
            user.updated_at = datetime.utcnow()
            db.commit()
            log.info(f"Existing user logged in: {user.email}")
            return {
                "id": str(user.id),
                "email": user.email,
                "name": user.full_name or user.username,
                "credits": user.credits,
                "is_new": False
            }
        else:
            # Create new user with 100 FREE credits
            new_user = User(
                email=google_user_data["email"],
                username=google_user_data.get("name", google_user_data["email"].split("@")[0]),
                full_name=google_user_data.get("name"),
                credits=100,  # 100 FREE CREDITS!
            )
            db.add(new_user)
            db.commit()
            db.refresh(new_user)
            log.info(f"New user created with 100 credits: {new_user.email}")
            return {
                "id": str(new_user.id),
                "email": new_user.email,
                "name": new_user.full_name,
                "credits": 100,
                "is_new": True
            }
    except Exception as e:
        db.rollback()
        log.error(f"Database error: {e}")
        raise
    finally:
        db.close()

# ============================================
# ROUTES
# ============================================

@router.post("/google/init", response_model=GoogleAuthInitResponse)
async def google_auth_init(request: GoogleAuthInitRequest):
    """
    Initialize Google OAuth flow
    Returns Google authorization URL
    """
    try:
        if not GOOGLE_CLIENT_ID:
            raise HTTPException(status_code=500, detail="Google OAuth not configured. Set GOOGLE_CLIENT_ID environment variable.")
        
        # Generate CSRF protection state
        state = secrets.token_urlsafe(32)
        oauth_states[state] = {
            "created_at": datetime.utcnow(),
            "redirect_url": request.redirect_url or f"{FRONTEND_URL}/api/auth/google/callback"
        }
        
        # Build Google OAuth URL
        redirect_uri = f"{FRONTEND_URL}/api/auth/google/callback"
        google_auth_url = (
            "https://accounts.google.com/o/oauth2/v2/auth?"
            f"client_id={GOOGLE_CLIENT_ID}&"
            f"redirect_uri={redirect_uri}&"
            "response_type=code&"
            "scope=openid email profile&"
            f"state={state}&"
            "access_type=offline&"
            "prompt=consent"
        )
        
        log.info(f"Generated Google OAuth URL with state: {state}")
        log.info(f"Redirect URI: {redirect_uri}")
        
        return GoogleAuthInitResponse(auth_url=google_auth_url)
        
    except Exception as e:
        log.error(f"Google OAuth init error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/google/callback")
async def google_auth_callback(code: str, state: str, error: Optional[str] = None):
    """
    Handle Google OAuth callback
    Exchange code for tokens and create session
    """
    try:
        # Check for errors
        if error:
            log.error(f"Google OAuth error: {error}")
            return RedirectResponse(url=f"{FRONTEND_URL}/login?error={error}")
        
        # Verify state (CSRF protection)
        if state not in oauth_states:
            log.error("Invalid state parameter")
            return RedirectResponse(url=f"{FRONTEND_URL}/login?error=invalid_state")
        
        # Clean up old states (older than 10 minutes)
        current_time = datetime.utcnow()
        oauth_states_copy = oauth_states.copy()
        for s, data in oauth_states_copy.items():
            if (current_time - data["created_at"]).seconds > 600:
                del oauth_states[s]
        
        # Exchange code for tokens
        token_url = "https://oauth2.googleapis.com/token"
        redirect_uri = f"{FRONTEND_URL}/api/auth/google/callback"
        
        token_data = {
            "code": code,
            "client_id": GOOGLE_CLIENT_ID,
            "client_secret": GOOGLE_CLIENT_SECRET,
            "redirect_uri": redirect_uri,
            "grant_type": "authorization_code"
        }
        
        async with httpx.AsyncClient() as client:
            token_response = await client.post(token_url, data=token_data)
            
            if token_response.status_code != 200:
                log.error(f"Token exchange failed: {token_response.text}")
                return RedirectResponse(url=f"{FRONTEND_URL}/login?error=token_exchange_failed")
            
            tokens = token_response.json()
            id_token_str = tokens.get("id_token")
            
            if not id_token_str:
                log.error("No ID token received")
                return RedirectResponse(url=f"{FRONTEND_URL}/login?error=no_id_token")
            
            # Verify and decode ID token
            try:
                idinfo = id_token.verify_oauth2_token(
                    id_token_str,
                    google_requests.Request(),
                    GOOGLE_CLIENT_ID
                )
            except ValueError as e:
                log.error(f"Invalid ID token: {e}")
                return RedirectResponse(url=f"{FRONTEND_URL}/login?error=invalid_token")
            
            # Extract user info
            google_user_data = {
                "id": idinfo["sub"],
                "email": idinfo["email"],
                "name": idinfo.get("name", idinfo["email"].split("@")[0]),
                "picture": idinfo.get("picture"),
                "email_verified": idinfo.get("email_verified", False)
            }
            
            # Get or create user
            user_data = await get_or_create_user(google_user_data)
            
            # Create JWT token
            access_token = create_jwt_token(user_data)
            
            # Remove used state
            del oauth_states[state]
            
            # Redirect to frontend with token
            redirect_url = f"{FRONTEND_URL}/api/auth/callback?token={access_token}"
            if user_data["is_new"]:
                redirect_url += "&new_user=true"
            
            log.info(f"Redirecting to: {redirect_url}")
            return RedirectResponse(url=redirect_url)
            
    except Exception as e:
        log.error(f"Google callback error: {e}")
        import traceback
        log.error(traceback.format_exc())
        return RedirectResponse(url=f"{FRONTEND_URL}/login?error=authentication_failed")

@router.post("/google/verify", response_model=AuthResponse)
async def verify_google_token(token: str):
    """
    Verify Google ID token (for client-side Google Sign-In)
    """
    try:
        # Verify token with Google
        idinfo = id_token.verify_oauth2_token(
            token,
            google_requests.Request(),
            GOOGLE_CLIENT_ID
        )
        
        # Extract user info
        google_user_data = {
            "id": idinfo["sub"],
            "email": idinfo["email"],
            "name": idinfo.get("name"),
            "picture": idinfo.get("picture"),
            "email_verified": idinfo.get("email_verified", False)
        }
        
        # Get or create user
        user_data = await get_or_create_user(google_user_data)
        
        # Create JWT token
        access_token = create_jwt_token(user_data)
        
        message = "Welcome! You've received 100 FREE credits! 🎉" if user_data["is_new"] else "Welcome back!"
        
        return AuthResponse(
            success=True,
            access_token=access_token,
            user=user_data,
            message=message
        )
        
    except ValueError as e:
        log.error(f"Invalid Google token: {e}")
        raise HTTPException(status_code=401, detail="Invalid Google token")
    except Exception as e:
        log.error(f"Token verification error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
