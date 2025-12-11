"""
Configuration management for TradeBerg Backend
"""
import os
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import field_validator

class Settings(BaseSettings):
    """Application settings"""
    
    # Server settings
    HOST: str = "0.0.0.0"
    PORT: int = 8080
    DEBUG: bool = False
    ENVIRONMENT: str = "development"
    
    # CORS settings for React frontend
    CORS_ORIGINS: str = ""
    
    # API Keys
    OPENAI_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""
    PERPLEXITY_API_KEY: str = ""
    GEMINI_API_KEY: str = ""
    ALPACA_API_KEY: Optional[str] = None
    ALPACA_SECRET_KEY: Optional[str] = None
    
    # Supabase
    SUPABASE_URL: str = ""
    SUPABASE_SERVICE_ROLE_KEY: str = ""
    SUPABASE_ANON_KEY: str = ""
    
    # Stripe
    STRIPE_SECRET_KEY: str = ""
    STRIPE_PUBLISHABLE_KEY: str = ""
    STRIPE_WEBHOOK_SECRET: str = ""
    STRIPE_PRICE_ID_PRO_MONTHLY: str = ""
    STRIPE_PRICE_ID_PRO_YEARLY: str = ""
    STRIPE_PRICE_ID_MAX_MONTHLY: str = ""
    STRIPE_PRICE_ID_MAX_YEARLY: str = ""
    
    # Database Configuration (Supabase PostgreSQL)
    # This will use the DATABASE_URL from env file, or fallback to Supabase
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres.pcxscejarxztezfeucgs:Treadburg%401@aws-0-us-east-1.pooler.supabase.com:5432/postgres?pgbouncer=true&sslmode=require"
    )
    
    # JWT
    JWT_SECRET_KEY: str = "your-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 24
    
    class Config:
        env_file = "env"  # Changed from .env to env (your actual file name)
        case_sensitive = True
        extra = "ignore"
    
    def get_cors_origins(self) -> List[str]:
        """Get CORS origins as a list"""
        if self.CORS_ORIGINS:
            return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]
        # Default CORS origins (development + production)
        return [
            "http://localhost:3000",
            "http://localhost:3002",  # Frontend running on port 3002
            "http://localhost:5173",
            "http://localhost:5174",
            "http://localhost:10000",  # Next.js dev server on port 10000
            "http://127.0.0.1:3000",
            "http://127.0.0.1:3002",
            "http://127.0.0.1:5173",
            "http://127.0.0.1:10000",
            "https://tradeberg-frontend-qwx0.onrender.com",  # Production frontend (current)
            "https://tradeberg-frontend.onrender.com",  # Production frontend (old)
            "https://supa.vercel.app",  # Alternative frontend
        ]

# Create settings instance
settings = Settings()
