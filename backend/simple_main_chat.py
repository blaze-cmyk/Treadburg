#!/usr/bin/env python3
"""
Simple replacement for main chat endpoint
Direct Perplexity integration for http://localhost:5173/ chat interface
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import requests
import time
import uvicorn

app = FastAPI(title="TradeBerg Main Chat")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/chat/completions")
@app.post("/api/v1/chat/completions")
@app.post("/api/tradeberg/chat/completions")
@app.post("/api/tradeberg/enforced/chat/completions")
async def main_chat_completions(request: Request):
    """Main chat endpoint for http://localhost:5173/ interface"""
    
    try:
        body = await request.json()
        print(f"📨 Main chat request: {body}")
        
        # Extract user message
        messages = body.get("messages", [])
        user_message = "hello"
        
        for msg in reversed(messages):
            if isinstance(msg, dict) and msg.get("role") == "user":
                content = msg.get("content", "")
                if isinstance(content, str):
                    user_message = content
                elif isinstance(content, list):
                    text_parts = [part.get("text", "") for part in content if part.get("type") == "text"]
                    user_message = " ".join(text_parts)
                break
        
        print(f"💬 Processing main chat: {user_message[:50]}...")
        
        # Direct Perplexity API call
        api_key = "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"
        
        # Enhanced prompt for analytics
        enhanced_prompt = f"Provide comprehensive financial market analytics and insights for: {user_message}. Include current market data, prices, trends, and actionable analysis. Be detailed and analytical."
        
        response = requests.post(
            "https://api.perplexity.ai/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "sonar-pro",
                "messages": [
                    {
                        "role": "system",
                        "content": "You are TRADEBERG - provide detailed financial analytics with real-time market data for ANY query. Always include prices, trends, and market insights."
                    },
                    {
                        "role": "user",
                        "content": enhanced_prompt
                    }
                ],
                "max_tokens": 2000,
                "temperature": 0.7
            },
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            analysis = result['choices'][0]['message']['content']
            
            # Format response for OpenAI compatibility
            formatted_response = f"**🔥 TRADEBERG ANALYTICS**\n\n{analysis}"
            
            # Create OpenAI-compatible response
            openai_response = {
                "id": f"chatcmpl-{int(time.time())}",
                "object": "chat.completion",
                "created": int(time.time()),
                "model": "gpt-4o",
                "choices": [{
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": formatted_response
                    },
                    "finish_reason": "stop"
                }],
                "usage": {
                    "prompt_tokens": result.get('usage', {}).get('total_tokens', 0) // 2,
                    "completion_tokens": result.get('usage', {}).get('total_tokens', 0) // 2,
                    "total_tokens": result.get('usage', {}).get('total_tokens', 0)
                }
            }
            
            print("✅ Main chat Perplexity response successful")
            return JSONResponse(content=openai_response, headers={"X-TradeBerg": "1"})
        else:
            print(f"❌ Perplexity API error: {response.status_code}")
            # Return fallback response
            fallback_response = {
                "id": f"chatcmpl-{int(time.time())}",
                "object": "chat.completion", 
                "created": int(time.time()),
                "model": "gpt-4o",
                "choices": [{
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": "**TRADEBERG**: Market analytics temporarily unavailable. Please try again."
                    },
                    "finish_reason": "stop"
                }],
                "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
            }
            return JSONResponse(content=fallback_response, headers={"X-TradeBerg": "1"})
            
    except Exception as e:
        print(f"❌ Main chat error: {e}")
        # Return fallback response
        fallback_response = {
            "id": f"chatcmpl-{int(time.time())}",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": "gpt-4o", 
            "choices": [{
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": "**TRADEBERG**: Providing market analytics... Please try your query again."
                },
                "finish_reason": "stop"
            }],
            "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
        }
        return JSONResponse(content=fallback_response, headers={"X-TradeBerg": "1"})

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "TradeBerg Main Chat"}

if __name__ == "__main__":
    print("🚀 Starting TradeBerg Main Chat Server on port 8083...")
    uvicorn.run(app, host="0.0.0.0", port=8083, log_level="info")
