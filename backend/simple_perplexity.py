#!/usr/bin/env python3
"""
Simple Perplexity API integration for TradeBerg
Direct API calls with no complex routing
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any
import requests
import uvicorn

app = FastAPI(title="TradeBerg Perplexity API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    model: str = "sonar-pro"
    temperature: float = 0.7

PERPLEXITY_API_KEY = "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"

@app.post("/api/tradeberg/enhanced-chat")
async def enhanced_chat(request: ChatRequest):
    """Direct Perplexity API integration for financial analysis"""
    
    try:
        # Get user message
        user_message = ""
        for msg in request.messages:
            if msg.role == "user":
                user_message = msg.content
                break
        
        if not user_message:
            return {
                "success": False,
                "error": "No user message found",
                "response": "Please provide a message to analyze."
            }
        
        print(f"Processing: {user_message[:50]}...")
        
        # Direct Perplexity API call
        url = "https://api.perplexity.ai/chat/completions"
        headers = {
            "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "sonar-pro",
            "messages": [
                {
                    "role": "system",
                    "content": "You are TRADEBERG - an institutional AI terminal with real-time market access. Provide comprehensive financial analysis with current market data, news, and actionable insights. Always include real-time prices, recent news, and market context. Format responses professionally with clear sections."
                },
                {
                    "role": "user",
                    "content": user_message
                }
            ],
            "max_tokens": 2000,
            "temperature": 0.7
        }
        
        response = requests.post(url, json=payload, headers=headers, timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            analysis = result['choices'][0]['message']['content']
            
            # Format response
            formatted_response = f"**🔥 TRADEBERG LIVE ANALYSIS**\n\n{analysis}\n\n---\n*Powered by Perplexity AI with real-time data*"
            
            return {
                "success": True,
                "response": formatted_response,
                "function_called": "perplexity_live_analysis",
                "usage": {"total_tokens": result.get('usage', {}).get('total_tokens', 0)}
            }
        else:
            print(f"Perplexity API error: {response.status_code} - {response.text}")
            return {
                "success": False,
                "error": f"Perplexity API error: {response.status_code}",
                "response": "TRADEBERG: Unable to get real-time market data right now. Please try again."
            }
        
    except Exception as e:
        print(f"Error: {e}")
        return {
            "success": False,
            "error": str(e),
            "response": "TRADEBERG: An error occurred. Please try again."
        }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "TradeBerg Perplexity API"}

if __name__ == "__main__":
    print("🚀 Starting TradeBerg Perplexity API on port 8082...")
    uvicorn.run(app, host="0.0.0.0", port=8082)
