"""
TradeBerg Backend API
Main FastAPI application for React frontend
"""
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware

from config import settings
from routes import api_router
from database import init_db

# Security middleware imports
from middleware.rate_limit import limiter, rate_limit_handler, SlowAPIMiddleware
from middleware.security import validate_request_size
from middleware.logging_config import SecurityLogger
from slowapi.errors import RateLimitExceeded

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    print("🚀 Starting TradeBerg Backend API...")
    print(f"📡 Environment: {settings.ENVIRONMENT}")
    print(f"🌐 CORS Origins: {settings.get_cors_origins()}")
    
    # Temporarily disabled database initialization - will connect when needed
    # init_db()
    print("⚠️  Database initialization skipped - will connect on first API call")

    # Temporarily disabled ingestion worker - requires Gemini API key
    # import asyncio
    # from core.ingestion.pipeline import pipeline
    # loop = asyncio.get_running_loop()
    # loop.create_task(pipeline.start(poll_interval=5))
    # print("👷 Ingestion Worker background task started")
    print("⚠️  Ingestion Worker disabled - requires GEMINI_API_KEY")
    
    
    yield
    # Shutdown
    print("👋 Shutting down TradeBerg Backend API...")

# Create FastAPI app
app = FastAPI(
    title="TradeBerg API",
    description="Backend API for TradeBerg Trading Platform",
    version="1.0.0",
    lifespan=lifespan
)

# Security: Rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_handler)
app.add_middleware(SlowAPIMiddleware)

# Security: Trusted hosts (prevent host header injection)
if settings.ENVIRONMENT == "production":
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["tradeberg.com", "*.tradeberg.com", "localhost"]
    )

# Security: Request size validation
class RequestSizeMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        await validate_request_size(request)
        response = await call_next(request)
        return response

app.add_middleware(RequestSizeMiddleware)

# Security: Add security headers
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        
        # Content Security Policy
        csp = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self' data:; "
            "connect-src 'self' https://pcxscejarxztezfeucgs.supabase.co;"
        )
        response.headers["Content-Security-Policy"] = csp
        
        return response
        port=settings.PORT,
        reload=settings.DEBUG
    )
