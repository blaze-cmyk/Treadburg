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
    """
    Get existing user or create new one with Supabase Auth + profile with 100 credits
    IMPORTANT: Users MUST be registered in Supabase Auth for verification
    """
    from services.supabase_service import get_supabase_client
    
    try:
        supabase = get_supabase_client()
        
        # First, try to get or create user in Supabase Auth
        # Check if user exists in auth.users
        try:
            # Try to get existing auth user by email
            auth_users = supabase.auth.admin.list_users()
            existing_auth_user = None
            
            if hasattr(auth_users, 'users'):
                for user in auth_users.users:
                    if user.email == google_user_data["email"]:
                        existing_auth_user = user
                        break
        except Exception as auth_error:
            log.warning(f"Could not check existing auth users: {auth_error}")
            existing_auth_user = None
        
        # If user doesn't exist in Supabase Auth, create them
        auth_user_id = None
        if not existing_auth_user:
            try:
                # Create user in Supabase Auth (for verification)
                auth_response = supabase.auth.admin.create_user({
                    "email": google_user_data["email"],
                    "email_confirm": True,  # Auto-confirm since Google verified
                    "user_metadata": {
                        "full_name": google_user_data.get("name"),
                        "avatar_url": google_user_data.get("picture"),
                        "provider": "google"
                    }
                })
                auth_user_id = auth_response.user.id if hasattr(auth_response, 'user') else None
                log.info(f"Created Supabase Auth user: {google_user_data['email']}")
            except Exception as auth_create_error:
                log.error(f"Failed to create Supabase Auth user: {auth_create_error}")
                # Continue anyway - we'll use profile table
        else:
            auth_user_id = existing_auth_user.id
            log.info(f"Found existing Supabase Auth user: {google_user_data['email']}")
        
        # Now handle the profiles table
        # Check if user exists in profiles table
        existing_profile = supabase.table('profiles').select('*').eq(
            'email', google_user_data["email"]
        ).execute()
        
        if existing_profile.data and len(existing_profile.data) > 0:
            # Update existing profile
            profile = existing_profile.data[0]
            
            update_data = {
                'updated_at': datetime.utcnow().isoformat()
            }
            
            # Update auth_user_id if we have it and it's not set
            if auth_user_id and not profile.get('auth_user_id'):
                update_data['auth_user_id'] = auth_user_id
            
            supabase.table('profiles').update(update_data).eq(
                'email', google_user_data["email"]
            ).execute()
            
            log.info(f"Existing user logged in: {profile['email']}")
            return {
                "id": str(profile.get('id', profile.get('auth_user_id', auth_user_id))),
                "email": profile['email'],
                "name": profile.get('full_name', google_user_data.get("name")),
                "credits": profile.get('credits_balance', 0),
                "is_new": False
            }
        else:
            # Create new profile with 100 FREE credits
            new_profile_data = {
                'email': google_user_data["email"],
                'full_name': google_user_data.get("name"),
                'is_verified': True,  # Google verified
                'credits_balance': 100,  # 100 FREE CREDITS!
                'total_credits_purchased': 0,
                'subscription_tier': 'free',
                'created_at': datetime.utcnow().isoformat(),
                'updated_at': datetime.utcnow().isoformat()
            }
            
            # Add auth_user_id if we have it
            if auth_user_id:
                new_profile_data['auth_user_id'] = auth_user_id
            
            result = supabase.table('profiles').insert(new_profile_data).execute()
            
            if result.data and len(result.data) > 0:
                new_profile = result.data[0]
                log.info(f"✅ New user created with 100 credits: {new_profile['email']}")
                log.info(f"✅ User registered in Supabase Auth: {auth_user_id}")
                return {
                    "id": str(new_profile.get('id', new_profile.get('auth_user_id', auth_user_id))),
                    "email": new_profile['email'],
                    "name": new_profile.get('full_name'),
                    "credits": 100,
                    "is_new": True
                }
            else:
                raise Exception("Failed to create user profile in database")
                
    except Exception as e:
        log.error(f"Database error: {e}")
        import traceback
        log.error(traceback.format_exc())
        raise

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
            "redirect_url": request.redirect_url
        }
        
        # Build Google OAuth URL - Google will redirect to BACKEND callback
        # Get backend URL from environment or construct it
        backend_url = os.getenv("BACKEND_URL", os.getenv("NEXT_PUBLIC_API_URL", "http://localhost:8080"))
        # Remove /api suffix if present
        if backend_url.endswith("/api"):
            backend_url = backend_url[:-4]
        
        redirect_uri = f"{backend_url}/api/auth/google/callback"
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
        
        # Get backend URL for redirect_uri (must match what we sent to Google)
        backend_url = os.getenv("BACKEND_URL", os.getenv("NEXT_PUBLIC_API_URL", "http://localhost:8080"))
        if backend_url.endswith("/api"):
            backend_url = backend_url[:-4]
        redirect_uri = f"{backend_url}/api/auth/google/callback"
        
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
