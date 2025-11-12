"""
Unified Vision API system for TradeBerg with multi-provider support
Supports OpenAI GPT-4o, Claude 3.5 Sonnet, Qwen-VL, DeepSeek-VL, and Perplexity
Includes caching, rate limiting, cost tracking, and automatic fallbacks
"""

import os
import base64
import hashlib
import time
import asyncio
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from collections import defaultdict

from open_webui.utils import logger
from open_webui.utils.vision_analyzer import analyze_chart_with_vision, analyze_chart_with_qwen
from open_webui.utils.perplexity_analyzer import analyze_chart_with_perplexity

log = logger.logger

# In-memory cache with TTL
_vision_cache = {}
_cache_timestamps = {}
_rate_limits = defaultdict(list)

# Cost tracking per provider (approximate costs per 1K tokens)
PROVIDER_COSTS = {
    "openai": 0.01,      # GPT-4o Vision ~$0.01/1K tokens
    "claude": 0.008,     # Claude 3.5 Sonnet ~$0.008/1K tokens  
    "qwen": 0.002,       # Qwen-VL ~$0.002/1K tokens
    "deepseek": 0.001,   # DeepSeek-VL ~$0.001/1K tokens
    "perplexity": 0.005  # Perplexity Sonar ~$0.005/1K tokens
}

# Rate limits per provider (requests per minute)
RATE_LIMITS = {
    "openai": 20,
    "claude": 20,
    "qwen": 30,
    "deepseek": 30,
    "perplexity": 20
}


def _generate_cache_key(symbol: str, timeframe: str, timestamp: int, prompt_hash: str) -> str:
    """Generate cache key for vision analysis."""
    return f"{symbol}:{timeframe}:{timestamp}:{prompt_hash}"


def _hash_prompt(prompt: str) -> str:
    """Generate hash for prompt to use in cache key."""
    return hashlib.md5(prompt.encode()).hexdigest()[:8]


def _is_rate_limited(provider: str) -> bool:
    """Check if provider is rate limited."""
    now = time.time()
    limit = RATE_LIMITS.get(provider, 20)
    
    # Clean old requests (older than 1 minute)
    _rate_limits[provider] = [req_time for req_time in _rate_limits[provider] if now - req_time < 60]
    
    # Check if we're at the limit
    return len(_rate_limits[provider]) >= limit


def _record_request(provider: str):
    """Record a request for rate limiting."""
    _rate_limits[provider].append(time.time())


def _clean_cache(max_entries: int = 100):
    """Clean old cache entries, keeping only the most recent."""
    if len(_vision_cache) > max_entries:
        # Sort by timestamp and keep only the most recent entries
        sorted_keys = sorted(_cache_timestamps.keys(), key=lambda k: _cache_timestamps[k], reverse=True)
        keys_to_keep = sorted_keys[:max_entries]
        
        # Remove old entries
        keys_to_remove = set(_vision_cache.keys()) - set(keys_to_keep)
        for key in keys_to_remove:
            _vision_cache.pop(key, None)
            _cache_timestamps.pop(key, None)


def _get_from_cache(cache_key: str, ttl_seconds: int = 300) -> Optional[Dict[str, Any]]:
    """Get analysis from cache if not expired."""
    if cache_key not in _vision_cache:
        return None
    
    # Check if expired
    cache_time = _cache_timestamps.get(cache_key, 0)
    if time.time() - cache_time > ttl_seconds:
        # Remove expired entry
        _vision_cache.pop(cache_key, None)
        _cache_timestamps.pop(cache_key, None)
        return None
    
    result = _vision_cache[cache_key].copy()
    result["from_cache"] = True
    return result


def _store_in_cache(cache_key: str, result: Dict[str, Any]):
    """Store analysis result in cache."""
    _vision_cache[cache_key] = result.copy()
    _cache_timestamps[cache_key] = time.time()
    _clean_cache()


async def analyze_chart_image(
    image_base64: str,
    user_prompt: str,
    symbol: str = "BTCUSDT",
    timeframe: str = "15m",
    provider: str = "auto",
    use_cache: bool = True,
    cache_ttl: int = 300
) -> Dict[str, Any]:
    """
    Unified chart analysis with multi-provider support and caching.
    
    Args:
        image_base64: Base64-encoded chart image
        user_prompt: User's analysis request
        symbol: Trading symbol
        timeframe: Chart timeframe
        provider: Vision provider ("auto", "openai", "claude", "qwen", "deepseek", "perplexity")
        use_cache: Enable caching
        cache_ttl: Cache TTL in seconds
        
    Returns:
        Dict with analysis, provider info, cost, caching status
    """
    start_time = time.time()
    
    # Generate cache key
    prompt_hash = _hash_prompt(user_prompt)
    timestamp_rounded = int(time.time() // cache_ttl) * cache_ttl  # Round to cache TTL
    cache_key = _generate_cache_key(symbol, timeframe, timestamp_rounded, prompt_hash)
    
    # Check cache first
    if use_cache:
        cached_result = _get_from_cache(cache_key, cache_ttl)
        if cached_result:
            log.info(f"✅ Returning cached vision analysis for {symbol}")
            return cached_result
    
    # Determine provider order
    if provider == "auto":
        # Auto fallback chain: Perplexity → OpenAI → Claude → Qwen → Error
        provider_chain = ["perplexity", "openai", "claude", "qwen"]
    else:
        provider_chain = [provider]
    
    # Try providers in order
    last_error = None
    for current_provider in provider_chain:
        try:
            # Check rate limiting
            if _is_rate_limited(current_provider):
                log.warning(f"⚠️ Rate limited for {current_provider}, trying next provider...")
                continue
            
            # Record request for rate limiting
            _record_request(current_provider)
            
            log.info(f"🔍 Analyzing chart with {current_provider} provider...")
            
            # Call appropriate provider
            if current_provider == "openai":
                result = await analyze_chart_with_vision(image_base64, user_prompt, symbol, "gpt-4o")
            elif current_provider == "claude":
                result = await analyze_chart_with_claude(image_base64, user_prompt, symbol)
            elif current_provider == "qwen":
                result = await analyze_chart_with_qwen(image_base64, user_prompt, symbol)
            elif current_provider == "deepseek":
                result = await analyze_chart_with_deepseek(image_base64, user_prompt, symbol)
            elif current_provider == "perplexity":
                result = await analyze_chart_with_perplexity(image_base64, user_prompt, symbol, "sonar-pro")
            else:
                raise ValueError(f"Unknown provider: {current_provider}")
            
            # Check if analysis was successful
            if result.get("error"):
                raise Exception(f"Provider {current_provider} returned error: {result.get('analysis', 'Unknown error')}")
            
            # Calculate cost and add metadata
            tokens_used = result.get("tokens_used", 1000)  # Default estimate
            cost_per_1k = PROVIDER_COSTS.get(current_provider, 0.01)
            estimated_cost = (tokens_used / 1000) * cost_per_1k
            
            enhanced_result = {
                **result,
                "provider": current_provider,
                "cost": estimated_cost,
                "from_cache": False,
                "success": True,
                "timestamp": datetime.now().isoformat(),
                "processing_time": time.time() - start_time
            }
            
            # Store in cache
            if use_cache:
                _store_in_cache(cache_key, enhanced_result)
            
            log.info(f"✅ Vision analysis complete with {current_provider} (${estimated_cost:.4f})")
            return enhanced_result
            
        except Exception as error:
            log.error(f"❌ {current_provider} provider failed: {error}")
            last_error = error
            continue
    
    # All providers failed
    log.error(f"❌ All vision providers failed. Last error: {last_error}")
    return {
        "analysis": f"TRADEBERG: Unable to analyze the chart for {symbol} right now. All vision providers are currently unavailable. Please try again later.",
        "error": True,
        "success": False,
        "provider": "none",
        "cost": 0,
        "from_cache": False,
        "timestamp": datetime.now().isoformat(),
        "last_error": str(last_error)
    }


async def analyze_chart_with_claude(
    screenshot: str,
    user_prompt: str,
    symbol: str = "BTCUSDT"
) -> Dict[str, Any]:
    """
    Analyzes chart screenshot using Anthropic Claude 3.5 Sonnet.
    """
    try:
        import anthropic
        
        log.info(f"🔍 Analyzing chart with Claude 3.5 Sonnet for {symbol}...")
        
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable not set")
        
        client = anthropic.Anthropic(api_key=api_key)
        
        # System prompt for trading analysis
        system_prompt = f"""You are TRADEBERG — an institutional AI terminal. Analyze this {symbol} chart with institutional precision.

CRITICAL RULES:
1. NEVER mention "screenshot", "image", "picture" in your response
2. Speak as if observing the live chart directly
3. Focus on liquidity zones, market structure, institutional positioning
4. Use professional trading terminology
5. Provide actionable entry/stop/target levels

Format: Brief overview → Liquidity Map → Path Scenarios → Trade Setup → Risk Management"""
        
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1000,
            system=system_prompt,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": f"Analyze this {symbol} chart: {user_prompt}"
                        },
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/png",
                                "data": screenshot
                            }
                        }
                    ]
                }
            ],
            temperature=0.7
        )
        
        analysis = response.content[0].text
        
        log.info("✅ Claude analysis complete")
        
        return {
            "analysis": analysis,
            "model": "claude-3-5-sonnet",
            "tokens_used": response.usage.input_tokens + response.usage.output_tokens,
            "symbol": symbol,
            "used_vision": True,
            "provider": "claude"
        }
        
    except Exception as error:
        log.error(f"❌ Claude Vision API error: {error}")
        
        return {
            "analysis": f"TRADEBERG: Unable to analyze the chart for {symbol} right now. Please try again.",
            "error": True,
            "used_vision": False,
            "provider": "claude"
        }


async def analyze_chart_with_deepseek(
    screenshot: str,
    user_prompt: str,
    symbol: str = "BTCUSDT"
) -> Dict[str, Any]:
    """
    Analyzes chart screenshot using DeepSeek-VL.
    """
    try:
        import httpx
        
        log.info(f"🔍 Analyzing chart with DeepSeek-VL for {symbol}...")
        
        api_key = os.getenv("DEEPSEEK_API_KEY")
        api_url = os.getenv("DEEPSEEK_API_URL", "https://api.deepseek.com/v1/chat/completions")
        
        if not api_key:
            raise ValueError("DEEPSEEK_API_KEY environment variable not set")
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                api_url,
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "deepseek-vl-chat",
                    "messages": [
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "text",
                                    "text": f"Analyze this {symbol} trading chart: {user_prompt}"
                                },
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:image/png;base64,{screenshot}"
                                    }
                                }
                            ]
                        }
                    ],
                    "max_tokens": 1000,
                    "temperature": 0.7
                }
            )
            
            response.raise_for_status()
            result = response.json()
            
            analysis = result["choices"][0]["message"]["content"]
            
            log.info("✅ DeepSeek-VL analysis complete")
            
            return {
                "analysis": f"TRADEBERG: {analysis}",
                "model": "deepseek-vl-chat",
                "tokens_used": result.get("usage", {}).get("total_tokens", 1000),
                "symbol": symbol,
                "used_vision": True,
                "provider": "deepseek"
            }
            
    except Exception as error:
        log.error(f"❌ DeepSeek-VL API error: {error}")
        
        return {
            "analysis": f"TRADEBERG: Unable to analyze the chart for {symbol} right now. Please try again.",
            "error": True,
            "used_vision": False,
            "provider": "deepseek"
        }


def get_cache_stats() -> Dict[str, Any]:
    """Get cache statistics."""
    now = time.time()
    active_entries = sum(1 for timestamp in _cache_timestamps.values() if now - timestamp < 300)
    
    return {
        "total_entries": len(_vision_cache),
        "active_entries": active_entries,
        "expired_entries": len(_vision_cache) - active_entries,
        "cache_size_mb": len(str(_vision_cache)) / (1024 * 1024),
        "rate_limit_status": {
            provider: len(requests) for provider, requests in _rate_limits.items()
        }
    }


def clear_cache():
    """Clear all cache entries."""
    global _vision_cache, _cache_timestamps
    _vision_cache.clear()
    _cache_timestamps.clear()
    log.info("🗑️ Vision API cache cleared")


# Export main functions
__all__ = [
    "analyze_chart_image",
    "get_cache_stats", 
    "clear_cache"
]
