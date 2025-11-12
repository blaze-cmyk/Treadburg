"""
Vision API Integration for Chart Analysis
Analyzes chart screenshots using OpenAI Vision API (or Qwen)
Screenshots are NEVER sent to chat UI - only used internally
"""

import os
from typing import Optional, Dict, Any
from openai import OpenAI

from open_webui.utils import logger

log = logger.logger


def get_openai_client() -> OpenAI:
    """Get OpenAI client instance."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable not set")
    return OpenAI(api_key=api_key)


async def analyze_chart_with_vision(
    screenshot: str,
    user_prompt: str,
    symbol: str = "BTCUSDT",
    model: str = "gpt-4o"
) -> Dict[str, Any]:
    """
    DISABLED: Vision analysis disabled to avoid OpenAI API usage.
    Returns error to indicate vision analysis is not available.
    """
    log.warning("🚫 Vision analysis disabled - OpenAI API not used")
    return {
        "error": "Vision analysis disabled",
        "analysis": "Vision analysis is currently disabled. Using Perplexity for market analysis instead.",
        "symbol": symbol,
        "used_vision": False
    }


async def analyze_chart_with_qwen(
    screenshot: str,
    user_prompt: str,
    symbol: str = "BTCUSDT"
) -> Dict[str, Any]:
    """
    Analyzes chart screenshot using Qwen Vision API (open-source alternative).
    
    Args:
        screenshot: Base64-encoded PNG image string
        user_prompt: Original user message/prompt
        symbol: Trading symbol being analyzed
        
    Returns:
        Dict with analysis text and metadata
    """
    try:
        import httpx
        
        log.info(f"🔍 Analyzing chart with Qwen Vision API for {symbol}...")
        
        qwen_api_key = os.getenv("QWEN_API_KEY")
        qwen_api_url = os.getenv("QWEN_API_URL", "https://dashscope.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation")
        
        if not qwen_api_key:
            raise ValueError("QWEN_API_KEY environment variable not set")
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                qwen_api_url,
                headers={
                    "Authorization": f"Bearer {qwen_api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "qwen-vl-max",
                    "input": {
                        "messages": [
                            {
                                "role": "user",
                                "content": [
                                    {
                                        "image": f"data:image/png;base64,{screenshot}"
                                    },
                                    {
                                        "text": f"Analyze this {symbol} chart: {user_prompt}"
                                    }
                                ]
                            }
                        ]
                    },
                    "parameters": {
                        "max_tokens": 1000,
                        "temperature": 0.7
                    }
                }
            )
            
            response.raise_for_status()
            result = response.json()
            
            analysis = result.get("output", {}).get("choices", [{}])[0].get("message", {}).get("content", "")
            
            log.info("✅ Qwen Vision analysis complete")
            
            return {
                "analysis": f"TRADEBERG: {analysis}",
                "model": "qwen-vl-max",
                "symbol": symbol,
                "used_vision": True
            }
            
    except Exception as error:
        log.error(f"❌ Qwen Vision API error: {error}")
        
        return {
            "analysis": f"TRADEBERG: Unable to analyze the chart for {symbol} right now. Please try again.",
            "error": True,
            "used_vision": False
        }

