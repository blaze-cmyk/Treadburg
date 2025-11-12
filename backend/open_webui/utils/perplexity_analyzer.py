"""
Perplexity API Integration for Chart Analysis with Market Context
Analyzes chart screenshots using Perplexity API with real-time market data
Screenshots are NEVER sent to chat UI - only used internally for analysis
"""

import os
import base64
import requests
from typing import Optional, Dict, Any

from open_webui.utils import logger

log = logger.logger


def get_perplexity_api_key() -> str:
    """Get Perplexity API key from environment."""
    api_key = os.getenv("PERPLEXITY_API_KEY")
    if not api_key:
        raise ValueError("PERPLEXITY_API_KEY environment variable not set")
    return api_key


async def analyze_chart_with_perplexity(
    screenshot: str,
    user_prompt: str,
    symbol: str = "BTCUSDT",
    model: str = "sonar-pro"
) -> Dict[str, Any]:
    """
    Analyzes chart screenshot using Perplexity API with real-time market context.
    
    CRITICAL: This screenshot is NEVER sent to chat UI.
    It's only used internally for analysis with live market data.
    
    Args:
        screenshot: Base64-encoded PNG image string
        user_prompt: Original user message/prompt
        symbol: Trading symbol being analyzed
        model: Perplexity model to use (default: sonar-pro)
        
    Returns:
        Dict with analysis text and metadata including market context
    """
    try:
        log.info(f"🔍 Analyzing chart with Perplexity API (with market context) for {symbol}...")
        
        api_key = get_perplexity_api_key()
        
        # Enhanced system prompt for trading analysis with market context
        system_prompt = f"""You are TRADEBERG — an institutional AI terminal with real-time market access. You combine technical chart analysis with live market intelligence.

CRITICAL RULES:
1. NEVER mention "screenshot", "image", "picture", "vision model", "I analyzed", or "I can see" in your response
2. Speak as if you're directly observing the live chart with real-time market data
3. Include current market context: recent news, whale activity, social sentiment, institutional flows
4. Focus on: liquidity zones, market structure, institutional positioning, macro context
5. Always include: current market bias, entry zones, stop levels, targets with rationale
6. Use institutional language: sweep, absorption, imbalance, trapped liquidity, basis, carry

Current symbol being analyzed: {symbol}

ENHANCED ANALYSIS FORMAT:
TRADEBERG: [Brief market overview with current context]

Market Context: [Recent news, institutional flows, macro factors affecting {symbol}]

Technical Structure: [Chart patterns, levels, volume, momentum]

Liquidity Map: [External pools, internal magnets, session extremes]

Institutional Positioning: [Large player activity, whale movements, basis/funding]

Path Scenarios: [Probability-weighted outcomes with beneficiaries/victims]

Trade Setup: [Entry zones, stops, targets, position sizing, risk management]

Market Intelligence: [Social sentiment, options flow, derivatives positioning]

Use real-time market data and news to enhance the technical analysis."""
        
        # Determine image MIME type
        mime_type = 'image/png'  # Default to PNG for screenshots
        
        url = "https://api.perplexity.ai/chat/completions"
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model,
            "messages": [
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": f"Analyze this {symbol} chart with current market context: {user_prompt}"
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{mime_type};base64,{screenshot}"
                            }
                        }
                    ]
                }
            ],
            "max_tokens": 1500,
            "temperature": 0.7
        }
        
        response = requests.post(url, json=payload, headers=headers, timeout=90)
        
        if response.status_code == 200:
            result = response.json()
            analysis = result['choices'][0]['message']['content']
            
            log.info("✅ Perplexity analysis complete with market context (result will be sent to user as text only)")
            
            # Return ONLY text with enhanced metadata
            return {
                "analysis": analysis,
                "model": model,
                "tokens_used": result.get('usage', {}).get('total_tokens', 0),
                "symbol": symbol,
                "used_vision": True,
                "provider": "perplexity",
                "has_market_context": True,
                "citations": result.get('citations', [])
            }
        else:
            log.error(f"❌ Perplexity API error: {response.status_code} - {response.text}")
            raise Exception(f"Perplexity API error: {response.status_code}")
            
    except Exception as error:
        log.error(f"❌ Perplexity Vision API error: {error}")
        
        # Fallback response if Perplexity fails
        return {
            "analysis": f"TRADEBERG: Unable to analyze the chart for {symbol} with market context right now due to a technical issue. Please try again or check the chart manually.",
            "error": True,
            "used_vision": False,
            "provider": "perplexity",
            "has_market_context": False
        }


async def analyze_chart_with_perplexity_context_only(
    user_prompt: str,
    symbol: str = "BTCUSDT",
    model: str = "sonar-pro"
) -> Dict[str, Any]:
    """
    Get market context analysis without chart image (for text-only queries).
    
    Args:
        user_prompt: User's market question/prompt
        symbol: Trading symbol being analyzed
        model: Perplexity model to use
        
    Returns:
        Dict with market context analysis
    """
    try:
        log.info(f"🔍 Getting market context from Perplexity for {symbol}...")
        
        api_key = get_perplexity_api_key()
        
        context_prompt = f"""You are TRADEBERG — an institutional AI terminal with real-time market access.

Provide current market intelligence for {symbol}:

Market Context: [Recent news, institutional flows, macro factors]
Sentiment Analysis: [Social sentiment, fear/greed indicators]
Institutional Activity: [Whale movements, large transactions, derivatives]
Technical Backdrop: [Key levels, trend context without chart analysis]
Risk Factors: [Upcoming events, volatility expectations]

Focus on actionable market intelligence that affects {symbol} trading decisions."""
        
        url = "https://api.perplexity.ai/chat/completions"
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model,
            "messages": [
                {
                    "role": "system",
                    "content": context_prompt
                },
                {
                    "role": "user",
                    "content": f"Provide current market context and intelligence for {symbol}: {user_prompt}"
                }
            ],
            "max_tokens": 1000,
            "temperature": 0.7
        }
        
        response = requests.post(url, json=payload, headers=headers, timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            analysis = result['choices'][0]['message']['content']
            
            log.info("✅ Perplexity market context analysis complete")
            
            return {
                "analysis": analysis,
                "model": model,
                "tokens_used": result.get('usage', {}).get('total_tokens', 0),
                "symbol": symbol,
                "used_vision": False,
                "provider": "perplexity",
                "has_market_context": True,
                "citations": result.get('citations', [])
            }
        else:
            log.error(f"❌ Perplexity API error: {response.status_code} - {response.text}")
            raise Exception(f"Perplexity API error: {response.status_code}")
            
    except Exception as error:
        log.error(f"❌ Perplexity market context error: {error}")
        
        return {
            "analysis": f"TRADEBERG: Unable to get current market context for {symbol} right now. Please try again.",
            "error": True,
            "used_vision": False,
            "provider": "perplexity",
            "has_market_context": False
        }
