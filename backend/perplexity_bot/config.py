"""
Configuration for Perplexity Trading Bot
"""
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # API Configuration
    PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY", "")
    PERPLEXITY_BASE_URL = "https://api.perplexity.ai"
    
    # Server Configuration
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", 8001))
    DEBUG = os.getenv("DEBUG", "false").lower() == "true"
    
    # CORS Configuration
    ALLOWED_ORIGINS = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8000"
    ]
    
    # Logging Configuration
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE = "logs/app.log"
    
    # Perplexity Model Configuration
    DEFAULT_MODEL = "sonar-pro"
    MAX_TOKENS = 4000
    TEMPERATURE = 0.2
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS = 60
    RATE_LIMIT_WINDOW = 60  # seconds

config = Config()
