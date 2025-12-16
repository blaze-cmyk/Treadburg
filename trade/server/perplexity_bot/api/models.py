"""
Request and Response models for Perplexity Trading Bot API
"""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class ChatMessage(BaseModel):
    """Individual chat message"""
    role: str = Field(..., description="Message role: user or assistant")
    content: str = Field(..., description="Message content")

class ChatRequest(BaseModel):
    """Request model for chat endpoint"""
    message: str = Field(..., description="User message")
    image_data: Optional[str] = Field(None, description="Base64 encoded image data")
    conversation_history: Optional[List[ChatMessage]] = Field(default_factory=list)
    model: Optional[str] = Field("sonar-pro", description="Perplexity model to use")
    temperature: Optional[float] = Field(0.2, ge=0.0, le=2.0)
    max_tokens: Optional[int] = Field(4000, ge=1, le=8000)

class Citation(BaseModel):
    """Citation from Perplexity response"""
    title: str
    url: str
    snippet: Optional[str] = None

class ChatResponse(BaseModel):
    """Response model for chat endpoint"""
    success: bool = Field(..., description="Whether the request was successful")
    message: str = Field(..., description="Assistant response")
    citations: Optional[List[Citation]] = Field(default_factory=list)
    related_questions: Optional[List[str]] = Field(default_factory=list)
    model_used: str = Field(..., description="Model that generated the response")
    tokens_used: Optional[int] = Field(None, description="Number of tokens used")
    processing_time: Optional[float] = Field(None, description="Processing time in seconds")
    error: Optional[str] = Field(None, description="Error message if any")

class HealthResponse(BaseModel):
    """Health check response"""
    status: str = Field(..., description="Service status")
    version: str = Field(..., description="Service version")
    timestamp: str = Field(..., description="Current timestamp")
    perplexity_api_configured: bool = Field(..., description="Whether Perplexity API is configured")

class ModelsResponse(BaseModel):
    """Available models response"""
    models: List[Dict[str, Any]] = Field(..., description="List of available models")
    default_model: str = Field(..., description="Default model")
