"""
Authentication routes - Complete Supabase Integration
All auth operations proxied through backend
"""
from fastapi import APIRouter, HTTPException, status, Header
from pydantic import BaseModel, EmailStr
from typing import Optional
import logging

from services.supabase_service import get_supabase_client

router = APIRouter()
log = logging.getLogger(__name__)

# ============================================
# REQUEST/RESPONSE MODELS
# ============================================

class SignupRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class GoogleAuthInitResponse(BaseModel):
    auth_url: str

class AuthResponse(BaseModel):
    success: bool
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    user: Optional[dict] = None
    message: Optional[str] = None

class SessionResponse(BaseModel):
    success: bool
    user: Optional[dict] = None
    message: Optional[str] = None

# ============================================
# SIGNUP ENDPOINT
# ============================================

@router.post("/signup", response_model=AuthResponse)
async def signup(request: SignupRequest):
    """
    Create new user account via Supabase
    Returns JWT tokens for immediate login
    Grants 100 FREE credits to new users!
    """
    try:
        supabase = get_supabase_client()
        
        # Create user in Supabase Auth
        auth_response = supabase.auth.sign_up({
            "email": request.email,
            "password": request.password,
            "options": {
                "data": {
                    "full_name": request.full_name or request.email.split('@')[0]
                }
            }
        })
        
        if not auth_response.user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Signup failed. Email may already be in use."
            )
        
        # Create user profile in database with 100 FREE credits!
        user_data = {
            'auth_user_id': auth_response.user.id,
            'email': request.email,
            'full_name': request.full_name or request.email.split('@')[0],
            'email_confirmed': False,
            'credits': 100,  # ← 100 FREE CREDITS for new users!
            'subscription_tier': 'free'
        }
        
        try:
            supabase.table('users').insert(user_data).execute()
            log.info(f"New user created with 100 free credits: {request.email}")
        except Exception as db_error:
            log.warning(f"User profile creation failed (may already exist): {db_error}")
        
        return AuthResponse(
            success=True,
            access_token=auth_response.session.access_token if auth_response.session else None,
            refresh_token=auth_response.session.refresh_token if auth_response.session else None,
            user={
                "id": auth_response.user.id,
                "email": auth_response.user.email,
                "full_name": request.full_name or request.email.split('@')[0],
                "email_confirmed": auth_response.user.email_confirmed_at is not None,
                "credits": 100,  # Show user they got 100 free credits!
                "subscription_tier": "free"
            },
            message="Signup successful! You've received 100 FREE credits to get started! 🎉"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Signup error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Signup failed: {str(e)}"
        )

# ============================================
# LOGIN ENDPOINT
# ============================================

@router.post("/login", response_model=AuthResponse)
async def login(request: LoginRequest):
    """
    Authenticate user with email/password via Supabase
    Returns JWT tokens
    """
    try:
        supabase = get_supabase_client()
        
        # Authenticate with Supabase
        auth_response = supabase.auth.sign_in_with_password({
            "email": request.email,
            "password": request.password
        })
        
        if not auth_response.user or not auth_response.session:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Get user profile from database
        user_profile = supabase.table('users').select('*').eq(
            'auth_user_id', auth_response.user.id
        ).execute()
        
        profile_data = user_profile.data[0] if user_profile.data else {}
        
        return AuthResponse(
            success=True,
            access_token=auth_response.session.access_token,
            refresh_token=auth_response.session.refresh_token,
            user={
                "id": auth_response.user.id,
                "email": auth_response.user.email,
                "full_name": profile_data.get('full_name') or auth_response.user.user_metadata.get('full_name'),
                "subscription_tier": profile_data.get('subscription_tier', 'free'),
                "credits": profile_data.get('credits', 0)
            },
            message="Login successful!"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login failed: {str(e)}"
        )

# ============================================
# GOOGLE OAUTH ENDPOINTS
# ============================================

@router.post("/google/init", response_model=GoogleAuthInitResponse)
async def google_auth_init(redirect_url: str = "http://localhost:3000/auth/callback"):
    """
    Initialize Google OAuth flow
    Returns authorization URL to redirect user to
    """
    try:
        supabase = get_supabase_client()
        
        # Generate OAuth URL
        auth_response = supabase.auth.sign_in_with_oauth({
            "provider": "google",
            "options": {
                "redirect_to": redirect_url
            }
        })
        
        return GoogleAuthInitResponse(
            auth_url=auth_response.url
        )
        
    except Exception as e:
        log.error(f"Google OAuth init error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to initialize Google auth: {str(e)}"
        )

@router.post("/google/callback", response_model=AuthResponse)
async def google_auth_callback(code: str):
    """
    Handle Google OAuth callback
    Exchange code for session tokens
    """
    try:
        supabase = get_supabase_client()
        
        # Exchange code for session
        auth_response = supabase.auth.exchange_code_for_session(code)
        
        if not auth_response.user or not auth_response.session:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Failed to authenticate with Google"
            )
        
        # Create/update user profile
        user_data = {
            'auth_user_id': auth_response.user.id,
            'email': auth_response.user.email,
            'full_name': auth_response.user.user_metadata.get('full_name'),
            'email_confirmed': True,
            'subscription_tier': 'free'
        }
        
        # Try to update existing user, or insert if not exists
        existing_user = supabase.table('users').select('*').eq(
            'auth_user_id', auth_response.user.id
        ).execute()
        
        if existing_user.data:
            # Update existing
            supabase.table('users').update(user_data).eq(
                'auth_user_id', auth_response.user.id
            ).execute()
        else:
            # Insert new
            user_data['credits'] = 0
            supabase.table('users').insert(user_data).execute()
        
        return AuthResponse(
            success=True,
            access_token=auth_response.session.access_token,
            refresh_token=auth_response.session.refresh_token,
            user={
                "id": auth_response.user.id,
                "email": auth_response.user.email,
                "full_name": auth_response.user.user_metadata.get('full_name'),
            },
            message="Google authentication successful!"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Google callback error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Google authentication failed: {str(e)}"
        )

# ============================================
# SESSION MANAGEMENT
# ============================================

@router.get("/session", response_model=SessionResponse)
async def get_session(authorization: Optional[str] = Header(None)):
    """
    Get current user session using JWT token
    """
    try:
        if not authorization or not authorization.startswith("Bearer "):
            return SessionResponse(
                success=False,
                message="No authorization token provided"
            )
        
        token = authorization.replace("Bearer ", "")
        supabase = get_supabase_client()
        
        # Verify token and get user
        user_response = supabase.auth.get_user(token)
        
        if not user_response.user:
            return SessionResponse(
                success=False,
                message="Invalid or expired token"
            )
        
        # Get user profile
        user_profile = supabase.table('users').select('*').eq(
            'auth_user_id', user_response.user.id
        ).execute()
        
        profile_data = user_profile.data[0] if user_profile.data else {}
        
        return SessionResponse(
            success=True,
            user={
                "id": user_response.user.id,
                "email": user_response.user.email,
                "full_name": profile_data.get('full_name') or user_response.user.user_metadata.get('full_name'),
                "subscription_tier": profile_data.get('subscription_tier', 'free'),
                "credits": profile_data.get('credits', 0)
            }
        )
        
    except Exception as e:
        log.error(f"Session error: {e}")
        return SessionResponse(
            success=False,
            message=f"Failed to get session: {str(e)}"
        )

# ============================================
# LOGOUT ENDPOINT
# ============================================

@router.post("/logout", response_model=AuthResponse)
async def logout(authorization: Optional[str] = Header(None)):
    """
    Logout user and invalidate session
    """
    try:
        if not authorization or not authorization.startswith("Bearer "):
            return AuthResponse(
                success=True,
                message="Already logged out"
            )
        
        token = authorization.replace("Bearer ", "")
        supabase = get_supabase_client()
        
        # Sign out from Supabase
        supabase.auth.sign_out()
        
        return AuthResponse(
            success=True,
            message="Logged out successfully"
        )
        
    except Exception as e:
        log.warning(f"Logout error (non-critical): {e}")
        return AuthResponse(
            success=True,
            message="Logged out"
        )
