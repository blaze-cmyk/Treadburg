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
            'is_verified': False,
            'credits_balance': 100,  # ← 100 FREE CREDITS for new users!
            'total_credits_purchased': 0,
            'subscription_tier': 'free'
        }
        
        try:
            supabase.table('profiles').insert(user_data).execute()
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
        user_profile = supabase.table('profiles').select('*').eq(
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
async def google_auth_init(redirect_url: str = "http://localhost:3000/api/auth/google/callback"):
    """
    Initialize Google OAuth flow with PKCE
    Returns authorization URL to redirect user to
    """
    try:
        supabase = get_supabase_client()
        
        log.info(f"Initializing Google OAuth with redirect_url: {redirect_url}")
        
        # Generate OAuth URL with PKCE flow (not implicit)
        auth_response = supabase.auth.sign_in_with_oauth({
            "provider": "google",
            "options": {
                "redirect_to": redirect_url,
                "skip_browser_redirect": True  # Return URL instead of redirecting
            }
        })
        
        log.info(f"Generated OAuth URL: {auth_response.url}")
        
        return GoogleAuthInitResponse(
            auth_url=auth_response.url
        )
        
    except Exception as e:
        log.error(f"Google OAuth init error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to initialize Google auth: {str(e)}"
        )

class GoogleCallbackRequest(BaseModel):
    code: str

@router.post("/google/callback", response_model=AuthResponse)
async def google_auth_callback(request: GoogleCallbackRequest):
    """
    Handle Google OAuth callback
    Exchange code for session tokens
    """
    try:
        supabase = get_supabase_client()
        
        log.info(f"Exchanging Google OAuth code for session")
        log.info(f"Code length: {len(request.code)}, Code preview: {request.code[:20]}...")
        
        # Exchange code for session using Supabase Python SDK
        # The method signature is: exchange_code_for_session({"auth_code": code})
        try:
            auth_response = supabase.auth.exchange_code_for_session({
                "auth_code": request.code
            })
        except Exception as exchange_error:
            log.error(f"Supabase exchange_code_for_session error: {exchange_error}")
            log.error(f"Error type: {type(exchange_error)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Failed to exchange code: {str(exchange_error)}"
            )
        
        log.info(f"Auth response type: {type(auth_response)}")
        
        # Check if response is an error string
        if isinstance(auth_response, str):
            log.error(f"Supabase returned error string: {auth_response}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Google authentication failed: {auth_response}"
            )
        
        # Handle different response structures from Supabase SDK
        user = None
        session = None
        
        if hasattr(auth_response, 'user'):
            user = auth_response.user
            session = auth_response.session
            log.info(f"Got user from object attributes: {user.id if hasattr(user, 'id') else 'unknown'}")
        elif isinstance(auth_response, dict):
            user = auth_response.get('user')
            session = auth_response.get('session')
            log.info(f"Got user from dict: {user.get('id') if user and isinstance(user, dict) else 'unknown'}")
        else:
            log.error(f"Unexpected auth response type: {type(auth_response)}, value: {auth_response}")
        
        if not user or not session:
            log.error(f"Missing user or session. User: {user}, Session: {session}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Failed to authenticate with Google - no user or session returned"
            )
        
        # Extract user data safely
        user_id = user.id if hasattr(user, 'id') else user.get('id')
        user_email = user.email if hasattr(user, 'email') else user.get('email')
        user_metadata = user.user_metadata if hasattr(user, 'user_metadata') else user.get('user_metadata', {})
        full_name = user_metadata.get('full_name') if isinstance(user_metadata, dict) else None
        
        # Create/update user profile
        user_data = {
            'auth_user_id': user_id,
            'email': user_email,
            'full_name': full_name,
            'is_verified': True,
            'subscription_tier': 'free'
        }
        
        # Try to update existing user, or insert if not exists
        try:
            existing_user = supabase.table('profiles').select('*').eq(
                'auth_user_id', user_id
            ).execute()
            
            if existing_user.data:
                # Update existing
                update_result = supabase.table('profiles').update(user_data).eq(
                    'auth_user_id', user_id
                ).execute()
                log.info(f"Updated existing user profile: {user_email}")
            else:
                # Insert new - grant 100 free credits on signup
                user_data['credits_balance'] = 100
                user_data['total_credits_purchased'] = 0
                insert_result = supabase.table('profiles').insert(user_data).execute()
                log.info(f"Created new user profile with 100 credits: {user_email}")
        except Exception as db_error:
            log.error(f"Database error creating/updating profile: {db_error}")
            # Continue anyway - user is authenticated, profile can be created later
            log.warning(f"Continuing with authentication despite profile error")
        
        # Extract session tokens safely
        access_token = session.access_token if hasattr(session, 'access_token') else session.get('access_token')
        refresh_token = session.refresh_token if hasattr(session, 'refresh_token') else session.get('refresh_token')
        
        if not access_token:
            log.error("No access token in session response")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to get access token from session"
            )
        
        return AuthResponse(
            success=True,
            access_token=access_token,
            refresh_token=refresh_token,
            user={
                "id": user_id,
                "email": user_email,
                "full_name": full_name,
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
# EMAIL VERIFICATION CALLBACK
# ============================================

class EmailCallbackRequest(BaseModel):
    code: str
    type: Optional[str] = None

@router.post("/email/callback", response_model=AuthResponse)
async def email_verification_callback(request: EmailCallbackRequest):
    """
    Handle email verification and password reset callbacks
    Exchange code for session tokens
    """
    try:
        supabase = get_supabase_client()
        
        log.info(f"Processing email callback, type: {request.type}")
        
        # Exchange code for session using correct method signature
        try:
            auth_response = supabase.auth.exchange_code_for_session({
                "auth_code": request.code
            })
        except Exception as exchange_error:
            log.error(f"Email callback exchange error: {exchange_error}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Failed to verify email: {str(exchange_error)}"
            )
        
        # Handle different response structures
        user = None
        session = None
        
        if hasattr(auth_response, 'user'):
            user = auth_response.user
            session = auth_response.session
        elif isinstance(auth_response, dict):
            user = auth_response.get('user')
            session = auth_response.get('session')
        
        if not user or not session:
            log.error(f"Invalid email callback response: {auth_response}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Failed to verify email"
            )
        
        # Extract user data safely
        user_id = user.id if hasattr(user, 'id') else user.get('id')
        user_email = user.email if hasattr(user, 'email') else user.get('email')
        
        # Update user profile to mark as verified
        supabase.table('profiles').update({
            'is_verified': True
        }).eq('auth_user_id', user_id).execute()
        
        log.info(f"Email verified for user: {user_email}")
        
        # Extract session tokens
        access_token = session.access_token if hasattr(session, 'access_token') else session.get('access_token')
        refresh_token = session.refresh_token if hasattr(session, 'refresh_token') else session.get('refresh_token')
        
        return AuthResponse(
            success=True,
            access_token=access_token,
            refresh_token=refresh_token,
            user={
                "id": user_id,
                "email": user_email,
            },
            message="Email verified successfully!"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Email callback error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Email verification failed: {str(e)}"
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
        user_profile = supabase.table('profiles').select('*').eq(
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
                "credits": profile_data.get('credits_balance', 0)
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
