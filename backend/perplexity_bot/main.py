"""
Perplexity Trading Bot - Isolated FastAPI Service

This is a completely separate service from OpenWeb UI to avoid middleware conflicts.
Runs on port 8001 by default.
"""
import logging
import uvicorn
from datetime import datetime
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

# Import our modules
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import config
from middleware.cors import setup_cors
from middleware.error_handler import (
    http_exception_handler,
    validation_exception_handler,
    general_exception_handler
)
from api.chat import router as chat_router
from services.perplexity_service import perplexity_service

# Setup logging
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL.upper()),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(config.LOG_FILE),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    logger.info("Starting Perplexity Trading Bot service...")
    logger.info(f"Perplexity API configured: {bool(config.PERPLEXITY_API_KEY)}")
    yield
    logger.info("Shutting down Perplexity Trading Bot service...")
    await perplexity_service.close()

# Create FastAPI app
app = FastAPI(
    title="Perplexity Trading Bot",
    description="Isolated FastAPI service for Perplexity-powered trading analysis",
    version="1.0.0",
    lifespan=lifespan
)

# Setup middleware
setup_cors(app)

# Setup error handlers
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# Add request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all requests"""
    start_time = datetime.now()
    
    # Log request
    logger.info(f"Request: {request.method} {request.url}")
    
    # Process request
    response = await call_next(request)
    
    # Log response
    process_time = (datetime.now() - start_time).total_seconds()
    logger.info(f"Response: {response.status_code} - {process_time:.3f}s")
    
    return response

# Include routers
app.include_router(chat_router, prefix="/api", tags=["chat"])

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Perplexity Trading Bot",
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.now().isoformat(),
        "endpoints": {
            "chat": "/api/chat",
            "health": "/api/health",
            "models": "/api/models"
        }
    }

# Health check at root level
@app.get("/health")
async def health():
    """Simple health check"""
    return {"status": "ok", "timestamp": datetime.now().isoformat()}

if __name__ == "__main__":
    logger.info(f"Starting server on {config.HOST}:{config.PORT}")
    uvicorn.run(
        "main:app",
        host=config.HOST,
        port=config.PORT,
        reload=config.DEBUG,
        log_level=config.LOG_LEVEL.lower()
    )
