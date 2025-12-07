"""
Security middleware for TradeBerg backend
Provides input validation, sanitization, and security utilities
"""
import re
import bleach
from typing import Any, Dict, Optional
from fastapi import HTTPException, Request
from pydantic import BaseModel, validator


class SecurityValidator:
    """Centralized security validation utilities"""
    
    # Allowed HTML tags for sanitization
    ALLOWED_TAGS = ['p', 'br', 'strong', 'em', 'u', 'a', 'ul', 'ol', 'li', 'code', 'pre']
    ALLOWED_ATTRIBUTES = {'a': ['href', 'title']}
    
    # Maximum lengths for inputs
    MAX_PROMPT_LENGTH = 10000
    MAX_TITLE_LENGTH = 200
    MAX_EMAIL_LENGTH = 255
    
    # Regex patterns
    EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    SQL_INJECTION_PATTERN = re.compile(r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|EXECUTE|UNION|DECLARE)\b)", re.IGNORECASE)
    XSS_PATTERN = re.compile(r'<script|javascript:|onerror=|onload=', re.IGNORECASE)
    PATH_TRAVERSAL_PATTERN = re.compile(r'\.\./|\.\.\\')
    
    @classmethod
    def sanitize_html(cls, text: str) -> str:
        """Sanitize HTML content to prevent XSS"""
        if not text:
            return ""
        return bleach.clean(
            text,
            tags=cls.ALLOWED_TAGS,
            attributes=cls.ALLOWED_ATTRIBUTES,
            strip=True
        )
    
    @classmethod
    def sanitize_text(cls, text: str) -> str:
        """Sanitize plain text input"""
        if not text:
            return ""
        
        # Remove null bytes
        text = text.replace('\x00', '')
        
        # Check for SQL injection patterns
        if cls.SQL_INJECTION_PATTERN.search(text):
            raise HTTPException(status_code=400, detail="Invalid input detected")
        
        # Check for XSS patterns
        if cls.XSS_PATTERN.search(text):
            raise HTTPException(status_code=400, detail="Invalid input detected")
        
        # Check for path traversal
        if cls.PATH_TRAVERSAL_PATTERN.search(text):
            raise HTTPException(status_code=400, detail="Invalid input detected")
        
        return text.strip()
    
    @classmethod
    def validate_email(cls, email: str) -> str:
        """Validate email format"""
        if not email or len(email) > cls.MAX_EMAIL_LENGTH:
            raise HTTPException(status_code=400, detail="Invalid email")
        
        if not cls.EMAIL_PATTERN.match(email):
            raise HTTPException(status_code=400, detail="Invalid email format")
        
        return email.lower().strip()
    
    @classmethod
    def validate_prompt(cls, prompt: str) -> str:
        """Validate and sanitize user prompts"""
        if not prompt:
            raise HTTPException(status_code=400, detail="Prompt cannot be empty")
        
        if len(prompt) > cls.MAX_PROMPT_LENGTH:
            raise HTTPException(status_code=400, detail=f"Prompt too long (max {cls.MAX_PROMPT_LENGTH} characters)")
        
        return cls.sanitize_text(prompt)
    
    @classmethod
    def validate_title(cls, title: str) -> str:
        """Validate and sanitize chat titles"""
        if not title:
            return "New Chat"
        
        if len(title) > cls.MAX_TITLE_LENGTH:
            title = title[:cls.MAX_TITLE_LENGTH]
        
        return cls.sanitize_text(title)
    
    @classmethod
    def validate_chat_id(cls, chat_id: str) -> str:
        """Validate UUID format for chat IDs"""
        # UUID pattern
        uuid_pattern = re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', re.IGNORECASE)
        
        if not uuid_pattern.match(chat_id):
            raise HTTPException(status_code=400, detail="Invalid chat ID format")
        
        return chat_id


class SecureRequest(BaseModel):
    """Base model with built-in validation"""
    
    @validator('*', pre=True)
    def sanitize_strings(cls, v):
        """Automatically sanitize all string fields"""
        if isinstance(v, str):
            return SecurityValidator.sanitize_text(v)
        return v


async def validate_request_size(request: Request, max_size: int = 10 * 1024 * 1024):
    """
    Middleware to validate request body size (default 10MB)
    Prevents large payload attacks
    """
    content_length = request.headers.get('content-length')
    
    if content_length:
        content_length = int(content_length)
        if content_length > max_size:
            raise HTTPException(
                status_code=413,
                detail=f"Request body too large (max {max_size} bytes)"
            )


def get_client_ip(request: Request) -> str:
    """Get real client IP address (handles proxies)"""
    # Check for forwarded IP (behind proxy/load balancer)
    forwarded = request.headers.get('X-Forwarded-For')
    if forwarded:
        return forwarded.split(',')[0].strip()
    
    # Check for real IP header
    real_ip = request.headers.get('X-Real-IP')
    if real_ip:
        return real_ip
    
    # Fallback to direct connection
    return request.client.host if request.client else "unknown"
