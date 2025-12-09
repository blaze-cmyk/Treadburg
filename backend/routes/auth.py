"""
Authentication routes - Handles all auth through Supabase
"""
from fastapi import APIRouter, HTTPException, Depends, Header
from pydantic import BaseModel, EmailStr
from typing import Optional
from services.supabase_client import get_supabase_client
import os

router = APIRouter()

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    username: Optional[str] = None
    full_name: Optional[str] = None

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict
    profile: dict

@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest):
    """User login endpoint - authenticates via Supabase"""
    try:
        supabase = get_supabase_client()
        
        # Sign in with Supabase
        response = supabase.auth.sign_in_with_password({
            "email": request.email,
            "password": request.password
        })
        
        if not response.user:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        # Get or create user profile
        profile_response = supabase.table('profiles').select('*').eq('auth_user_id', response.user.id).execute()
        
        if not profile_response.data:
            # Create profile if doesn't exist
            profile_data = {
                'auth_user_id': response.user.id,
                'email': response.user.email,
                'full_name': response.user.user_metadata.get('full_name', request.email.split('@')[0]),
                'subscription_tier': 'free',
                'credits_balance': 0,
                'is_active': True,
                'is_verified': response.user.email_confirmed_at is not None
            }
            profile_response = supabase.table('profiles').insert(profile_data).execute()
        
        profile = profile_response.data[0] if profile_response.data else {}
        
        return TokenResponse(
            access_token=response.session.access_token,
            token_type="bearer",
            user={
                "id": response.user.id,
                "email": response.user.email,
                "email_confirmed_at": response.user.email_confirmed_at
            },
            profile=profile
        )
        
    except Exception as e:
        print(f"Login error: {str(e)}")
        raise HTTPException(status_code=401, detail=str(e))

@router.post("/register", response_model=TokenResponse)
async def register(request: RegisterRequest):
    """User registration endpoint - creates user in Supabase"""
    try:
        supabase = get_supabase_client()
        
        # Sign up with Supabase
        response = supabase.auth.sign_up({
            "email": request.email,
            "password": request.password,
            "options": {
                "data": {
                    "full_name": request.full_name or request.username or request.email.split('@')[0]
                }
            }
        })
        
        if not response.user:
            raise HTTPException(status_code=400, detail="Registration failed")
        
        # Create user profile
        profile_data = {
            'auth_user_id': response.user.id,
            'email': response.user.email,
            'full_name': request.full_name or request.username or request.email.split('@')[0],
            'subscription_tier': 'free',
            'credits_balance': 100,  # Free tier gets 100 credits
            'is_active': True,
            'is_verified': False
        }
        
        profile_response = supabase.table('profiles').insert(profile_data).execute()
        profile = profile_response.data[0] if profile_response.data else {}
        
        return TokenResponse(
            access_token=response.session.access_token if response.session else "",
            token_type="bearer",
            user={
                "id": response.user.id,
                "email": response.user.email,
                "email_confirmed_at": response.user.email_confirmed_at
            },
            profile=profile
        )
        
    except Exception as e:
        print(f"Registration error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/logout")
async def logout(authorization: Optional[str] = Header(None)):
    """User logout endpoint"""
    try:
        if authorization and authorization.startswith("Bearer "):
            token = authorization.split(" ")[1]
            supabase = get_supabase_client()
            supabase.auth.sign_out()
        
        return {"message": "Logged out successfully"}
    except Exception as e:
        return {"message": "Logged out successfully"}

@router.get("/me")
async def get_current_user(authorization: Optional[str] = Header(None)):
    """Get current user information"""
    try:
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Not authenticated")
        
        token = authorization.split(" ")[1]
        supabase = get_supabase_client()
        
        # Get user from token
        user_response = supabase.auth.get_user(token)
        
        if not user_response.user:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        # Get profile
        profile_response = supabase.table('profiles').select('*').eq('auth_user_id', user_response.user.id).execute()
        profile = profile_response.data[0] if profile_response.data else {}
        
        return {
            "user": {
                "id": user_response.user.id,
                "email": user_response.user.email,
                "email_confirmed_at": user_response.user.email_confirmed_at
            },
            "profile": profile
        }
        
    except Exception as e:
        print(f"Get user error: {str(e)}")
        raise HTTPException(status_code=401, detail=str(e))

class UpdateProfileRequest(BaseModel):
    full_name: Optional[str] = None
    bio: Optional[str] = None
    country: Optional[str] = None
    phone: Optional[str] = None
    avatar_url: Optional[str] = None
    timezone: Optional[str] = None
    language: Optional[str] = None

@router.put("/profile")
async def update_profile(
    request: UpdateProfileRequest,
    authorization: Optional[str] = Header(None)
):
    """Update user profile"""
    try:
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Not authenticated")
        
        token = authorization.split(" ")[1]
        supabase = get_supabase_client()
        
        # Get user from token
        user_response = supabase.auth.get_user(token)
        
        if not user_response.user:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        # Prepare update data
        update_data = request.dict(exclude_none=True)
        if update_data:
            update_data['updated_at'] = 'now()'
            
            # Update profile in database
            response = supabase.table('profiles').update(update_data).eq('auth_user_id', user_response.user.id).execute()
            
            if response.data:
                return {
                    "message": "Profile updated successfully",
                    "profile": response.data[0]
                }
            else:
                raise HTTPException(status_code=400, detail="Failed to update profile")
        else:
            raise HTTPException(status_code=400, detail="No data to update")
            
    except Exception as e:
        print(f"Update profile error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

class ResetPasswordRequest(BaseModel):
    email: EmailStr

class UpdatePasswordRequest(BaseModel):
    new_password: str

@router.post("/reset-password")
async def reset_password(request: ResetPasswordRequest):
    """Send password reset email"""
    try:
        supabase = get_supabase_client()
        
        # Send password reset email
        response = supabase.auth.reset_password_email(request.email)
        
        return {
            "message": "Password reset email sent. Please check your inbox."
        }
        
    except Exception as e:
        print(f"Reset password error: {str(e)}")
        # Don't reveal if email exists or not for security
        return {
            "message": "If the email exists, a password reset link has been sent."
        }

@router.post("/update-password")
async def update_password(
    request: UpdatePasswordRequest,
    authorization: Optional[str] = Header(None)
):
    """Update user password"""
    try:
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Not authenticated")
        
        token = authorization.split(" ")[1]
        supabase = get_supabase_client()
        
        # Update password
        response = supabase.auth.update_user({
            "password": request.new_password
        })
        
        return {
            "message": "Password updated successfully"
        }
        
    except Exception as e:
        print(f"Update password error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

