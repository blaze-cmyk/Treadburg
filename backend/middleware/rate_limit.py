"""
Rate limiting middleware for TradeBerg backend
Protects against DDoS and brute force attacks
"""
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from fastapi import Request, Response
from typing import Callable


# Initialize rate limiter
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["100/minute"],  # Global limit: 100 requests per minute
    storage_uri="memory://",  # Use in-memory storage (upgrade to Redis for production)
    headers_enabled=True  # Include rate limit info in response headers
)


# Custom rate limit handler
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    """Custom handler for rate limit exceeded"""
    return Response(
        content="Rate limit exceeded. Please try again later.",
        status_code=429,
        headers={
            "Retry-After": str(exc.detail.split("Retry after ")[1].split(" ")[0]) if "Retry after" in exc.detail else "60",
            "X-RateLimit-Limit": "100",
            "X-RateLimit-Remaining": "0",
        }
    )


# Rate limit configurations for different endpoints
RATE_LIMITS = {
    # Authentication endpoints - strict limits
    "auth_login": "10/minute",
    "auth_signup": "5/minute",
    "auth_reset": "3/minute",
    
    # Chat endpoints - moderate limits
    "chat_create": "20/minute",
    "chat_message": "30/minute",  # AI generation is expensive
    "chat_list": "60/minute",
    
    # General API - lenient limits
    "api_general": "100/minute",
}


def get_rate_limit(endpoint_type: str = "api_general") -> str:
    """Get rate limit for specific endpoint type"""
    return RATE_LIMITS.get(endpoint_type, "100/minute")
