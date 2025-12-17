"""
Direct Google OAuth 2.0 Implementation (No Supabase)
Handles Google authentication flow with JWT tokens
"""
from fastapi import APIRouter, HTTPException, status, Request
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, EmailStr
from typing import Optional
import logging
import secrets
import jwt
from datetime import datetime, timedelta
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
import os

router = APIRouter()
log = logging.getLogger(__name__)

# Configuration
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:3000/api/auth/callback/google")
JWT_SECRET = os.getenv("JWT_SECRET", secrets.token_urlsafe(32))
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24

# In-memory storage for OAuth state (use Redis in production)
oauth_states = {}

# ============================================
# MODELS
# ============================================

class GoogleAuthInitResponse(BaseModel):
    auth_url: str

class AuthResponse(BaseModel):
    success: bool
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    user: Optional[dict] = None
    message: Optional[str] = None

class TokenVerifyRequest(BaseModel):
    token: str

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

def verify_jwt_token(token: str) -> dict:
    """Verify and decode JWT token"""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

def save_user_to_db(user_data: dict):
    """
    Save or update user in database
    TODO: Implement your database logic here (PostgreSQL, MongoDB, etc.)
    """
    # Example structure - replace with your actual database
    from services.database import get_db_connection
    
    try:
        db = get_db_connection()
        
        # Check if user exists
        existing_user = db.execute(
            "SELECT * FROM users WHERE email = ?", (user_data["email"],)
        ).fetchone()
        
        if existing_user:
            # Update existing user
            db.execute(
                """UPDATE users 
                   SET name = ?, picture = ?, last_login = ? 
                   WHERE email = ?""",
                (user_data["name"], user_data.get("picture"), datetime.utcnow(), user_data["email"])
            )
            user_id = existing_user["id"]
        else:
            # Create new user with 100 free credits
            cursor = db.execute(
                """INSERT INTO users (email, name, picture, credits_balance, subscription_tier, created_at) 
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (user_data["email"], user_data["name"], user_data.get("picture"), 
                 100, "free", datetime.utcnow())
            )
            user_id = cursor.lastrowid
            log.info(f"New user created with 100 free credits: {user_data['email']}")
        
        db.commit()
        return user_id
        
    except Exception as e:
        log.error(f"Database error: {e}")
        # Continue even if DB fails - user can still authenticate
        return user_data.get("sub")

# ============================================
# GOOGLE OAUTH ENDPOINTS
# ============================================

@router.get("/google/init")
async def google_auth_init(redirect_uri: Optional[str] = None):
    """
    Initialize Google OAuth flow
    Returns authorization URL to redirect user to
    """
    try:
        if not GOOGLE_CLIENT_ID:
            raise HTTPException(
                status_code=500,
                detail="Google OAuth not configured. Set GOOGLE_CLIENT_ID environment variable."
            )
        
        # Generate random state for CSRF protection
        state = secrets.token_urlsafe(32)
        oauth_states[state] = {
            "created_at": datetime.utcnow(),
            "redirect_uri": redirect_uri or GOOGLE_REDIRECT_URI
        }
        
        # Build Google OAuth URL
        google_auth_url = (
            "https://accounts.google.com/o/oauth2/v2/auth?"
            f"client_id={GOOGLE_CLIENT_ID}&"
            f"redirect_uri={GOOGLE_REDIRECT_URI}&"
            "response_type=code&"
            "scope=openid email profile&"
            f"state={state}&"
            "access_type=offline&"
            "prompt=consent"
        )
        
        log.info(f"Generated Google OAuth URL with state: {state}")
        
        return GoogleAuthInitResponse(auth_url=google_auth_url)
        
    except Exception as e:
        log.error(f"Google OAuth init error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to initialize Google auth: {str(e)}"
        )

@router.get("/google/callback")
async def google_auth_callback(code: str, state: str, error: Optional[str] = None):
    """
    Handle Google OAuth callback
    Exchange authorization code for tokens and user info
    """
    try:
        # Check for OAuth errors
        if error:
            log.error(f"Google OAuth error: {error}")
            raise HTTPException(status_code=400, detail=f"Google authentication failed: {error}")
        
        # Verify state to prevent CSRF
        if state not in oauth_states:
            raise HTTPException(status_code=400, detail="Invalid state parameter")
        
        # Clean up old states (older than 10 minutes)
        current_time = datetime.utcnow()
        oauth_states_copy = oauth_states.copy()
        for s, data in oauth_states_copy.items():
            if (current_time - data["created_at"]).seconds > 600:
                del oauth_states[s]
        
        # Exchange code for tokens
        import httpx
        
        token_url = "https://oauth2.googleapis.com/token"
        token_data = {
            "code": code,
            "client_id": GOOGLE_CLIENT_ID,
            "client_secret": GOOGLE_CLIENT_SECRET,
            "redirect_uri": GOOGLE_REDIRECT_URI,
            "grant_type": "authorization_code"
        }
        
        async with httpx.AsyncClient() as client:
            token_response = await client.post(token_url, data=token_data)
            
            if token_response.status_code != 200:
                log.error(f"Token exchange failed: {token_response.text}")
                raise HTTPException(status_code=400, detail="Failed to exchange code for tokens")
            
            tokens = token_response.json()
            id_token_str = tokens.get("id_token")
            
            if not id_token_str:
                raise HTTPException(status_code=400, detail="No ID token received")
            
            # Verify and decode ID token
            try:
                idinfo = id_token.verify_oauth2_token(
                    id_token_str, 
                    google_requests.Request(), 
                    GOOGLE_CLIENT_ID
                )
                
                # Extract user info
                user_data = {
                    "id": idinfo["sub"],
                    "email": idinfo["email"],
                    "name": idinfo.get("name", idinfo["email"].split("@")[0]),
                    "picture": idinfo.get("picture"),
                    "email_verified": idinfo.get("email_verified", False)
                }
                
                # Save user to database
                save_user_to_db(user_data)
                
                # Create JWT token
                access_token = create_jwt_token(user_data)
                
                # Remove used state
                del oauth_states[state]
                
                # Redirect to frontend with token
                frontend_url = os.getenv("NEXT_PUBLIC_APP_URL", "http://localhost:3000")
                redirect_url = f"{frontend_url}/auth/callback?token={access_token}"
                
                return RedirectResponse(url=redirect_url)
                
            except ValueError as e:
                log.error(f"Invalid ID token: {e}")
                raise HTTPException(status_code=400, detail="Invalid ID token")
        
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Google callback error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Google authentication failed: {str(e)}"
        )

@router.post("/google/verify", response_model=AuthResponse)
async def verify_google_token(request: TokenVerifyRequest):
    """
    Verify Google ID token directly (for client-side Google Sign-In)
    """
    try:
        # Verify the token with Google
        idinfo = id_token.verify_oauth2_token(
            request.token, 
            google_requests.Request(), 
            GOOGLE_CLIENT_ID
        )
        
        # Extract user info
        user_data = {
            "id": idinfo["sub"],
            "email": idinfo["email"],
            "name": idinfo.get("name", idinfo["email"].split("@")[0]),
            "picture": idinfo.get("picture"),
            "email_verified": idinfo.get("email_verified", False)
        }
        
        # Save user to database
        save_user_to_db(user_data)
        
        # Create JWT token
        access_token = create_jwt_token(user_data)
        
        return AuthResponse(
            success=True,
            access_token=access_token,
            user=user_data,
            message="Google authentication successful!"
        )
        
    except ValueError as e:
        log.error(f"Invalid Google token: {e}")
        raise HTTPException(status_code=401, detail="Invalid Google token")
    except Exception as e:
        log.error(f"Token verification error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to verify token: {str(e)}"
        )

# ============================================
# SESSION MANAGEMENT
# ============================================

@router.post("/verify-token", response_model=AuthResponse)
async def verify_token(request: TokenVerifyRequest):
    """Verify JWT token and return user data"""
    try:
        payload = verify_jwt_token(request.token)
        
        return AuthResponse(
            success=True,
            user={
                "id": payload["user_id"],
                "email": payload["email"],
                "name": payload.get("name")
            },
            message="Token is valid"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Token verification error: {e}")
        raise HTTPException(status_code=401, detail="Invalid token")

@router.post("/logout")
async def logout():
    """Logout endpoint (client-side token removal)"""
    return {"success": True, "message": "Logged out successfully"}
