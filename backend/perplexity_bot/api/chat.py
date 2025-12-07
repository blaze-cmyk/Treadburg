"""
Chat API endpoints for Perplexity Trading Bot
"""
import logging
from datetime import datetime
from fastapi import APIRouter, HTTPException
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.models import ChatRequest, ChatResponse, HealthResponse, ModelsResponse
from services.perplexity_service import perplexity_service
from config import config

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """
    Main chat endpoint for Perplexity trading analysis
    """
    try:
        logger.info(f"Processing chat request: {request.message[:100]}...")
        
        # Process the message through Perplexity service
        result = await perplexity_service.process_message(
            message=request.message,
            image_data=request.image_data,
            conversation_history=[msg.dict() for msg in request.conversation_history],
            model=request.model,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            # Default to full analysis mode for the standalone bot API
            mode="analysis",
            context=None,
        )
        
        # Return structured response
        return ChatResponse(**result)
        
    except Exception as e:
        logger.error(f"Chat endpoint error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process chat request: {str(e)}"
        )

@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint
    """
    return HealthResponse(
        status="ok",
        version="1.0.0",
        timestamp=datetime.now().isoformat(),
        perplexity_api_configured=bool(config.PERPLEXITY_API_KEY)
    )

@router.get("/models", response_model=ModelsResponse)
async def get_models():
    """
    Get available models
    """
    models = [
        {
            "id": "sonar-pro",
            "name": "Sonar Pro",
            "description": "Advanced model for comprehensive analysis",
            "max_tokens": 4000
        },
        {
            "id": "sonar",
            "name": "Sonar",
            "description": "Standard model for general queries",
            "max_tokens": 4000
        }
    ]
    
    return ModelsResponse(
        models=models,
        default_model=config.DEFAULT_MODEL
    )
