#!/usr/bin/env python3
"""
Minimal Perplexity API server for TradeBerg
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import requests
import uvicorn

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/tradeberg/enhanced-chat")
async def chat():
    """Minimal Perplexity chat endpoint"""
    
    api_key = "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"
    
    try:
        response = requests.post(
            "https://api.perplexity.ai/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "sonar-pro",
                "messages": [
                    {"role": "system", "content": "You are TRADEBERG - provide financial analysis with real-time data."},
                    {"role": "user", "content": "List all major news headlines affecting JPMorgan Chase in the last 48 hours"}
                ],
                "max_tokens": 1000
            },
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            analysis = result['choices'][0]['message']['content']
            
            return {
                "success": True,
                "response": f"**TRADEBERG ANALYSIS**\n\n{analysis}",
                "function_called": "perplexity_analysis"
            }
        else:
            return {
                "success": False,
                "error": f"API Error: {response.status_code}",
                "response": "Error getting data"
            }
            
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "response": "Error occurred"
        }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8082)
