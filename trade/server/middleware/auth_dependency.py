"""
Authentication Dependency
Extracts user JWT token from Authorization header
"""
from fastapi import Header, HTTPException, status
from typing import Optional

async def get_user_token(authorization: Optional[str] = Header(None)) -> Optional[str]:
    """
    Extract user JWT token from Authorization header
    
    Args:
        authorization: Authorization header value
    
    Returns:
        JWT token string or None
    
    Raises:
        HTTPException: If authorization header is malformed
    """
    if not authorization:
        return None
    
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format. Expected 'Bearer <token>'"
        )
    
    token = authorization.replace("Bearer ", "").strip()
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No token provided in authorization header"
        )
    
    return token


async def require_user_token(authorization: Optional[str] = Header(None)) -> str:
    """
    Require user JWT token from Authorization header
    
    Args:
        authorization: Authorization header value
    
    Returns:
        JWT token string
    
    Raises:
        HTTPException: If no token provided or malformed
    """
    token = await get_user_token(authorization)
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required. Please provide a valid JWT token."
        )
    
    return token
