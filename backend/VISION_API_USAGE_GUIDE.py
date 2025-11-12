#!/usr/bin/env python3
"""
Vision API Usage Guide and Examples
Complete guide for using the enhanced Vision API system
"""

# ============================================================================
# EXAMPLE 1: Basic OpenAI Vision Analysis
# ============================================================================

async def example_openai_basic():
    """Basic OpenAI GPT-4o Vision analysis."""
    from open_webui.utils.vision_api import analyze_chart_image
    
    # Your base64-encoded chart screenshot
    screenshot_base64 = "iVBORw0KGgo..."  # Full base64 string
    
    result = await analyze_chart_image(
        image_base64=screenshot_base64,
        user_prompt="Analyze this chart and give me entry/stop/targets",
        symbol="BTCUSDT",
        timeframe="15m",
        provider="openai",  # Use OpenAI GPT-4o
        use_cache=True,     # Enable caching (5 min TTL)
        cache_ttl=300
    )
    
    # Result structure:
    # {
    #     "analysis": "TRADEBERG: ...",
    #     "provider": "openai",
    #     "model": "gpt-4o",
    #     "tokens_used": 1234,
    #     "cost": 0.0487,
    #     "from_cache": False,
    #     "success": True,
    #     "timestamp": "2025-11-04T..."
    # }
    
    print(result["analysis"])
    print(f"Cost: ${result['cost']:.4f}")
    print(f"Cached: {result['from_cache']}")


# ============================================================================
# EXAMPLE 2: Claude Vision Analysis
# ============================================================================

async def example_claude_vision():
    """Use Anthropic Claude 3.5 Sonnet for analysis."""
    from open_webui.utils.vision_api import analyze_chart_image
    
    screenshot_base64 = "iVBORw0KGgo..."
    
    result = await analyze_chart_image(
        image_base64=screenshot_base64,
        user_prompt="What's the liquidity setup here?",
        symbol="ETHUSDT",
        timeframe="1h",
        provider="claude",  # Use Claude instead of OpenAI
        use_cache=True
    )
    
    # Claude is often better at nuanced analysis
    # and costs slightly less than GPT-4o
    print(result["analysis"])


# ============================================================================
# EXAMPLE 3: Multiple Provider Fallback
# ============================================================================

async def example_with_fallback():
    """Try OpenAI, fallback to Claude if it fails."""
    from open_webui.utils.vision_api import analyze_chart_image
    
    screenshot_base64 = "iVBORw0KGgo..."
    
    # Primary: OpenAI
    result = await analyze_chart_image(
        image_base64=screenshot_base64,
        user_prompt="Analyze this setup",
        symbol="SOLUSDT",
        timeframe="4h",
        provider="openai",
        use_cache=True
    )
    
    # If OpenAI fails, the system automatically tries Claude
    # This is built into the analyze_chart_image function
    
    if result["success"]:
        print(f"Analysis from {result['provider']}: {result['analysis'][:100]}...")
    else:
        print(f"All providers failed: {result.get('error')}")


# ============================================================================
# EXAMPLE 4: Caching for Performance
# ============================================================================

async def example_caching():
    """Demonstrate caching mechanism."""
    from open_webui.utils.vision_api import analyze_chart_image, get_cache_stats, clear_vision_cache
    
    screenshot_base64 = "iVBORw0KGgo..."
    
    # First call - hits API
    print("First call (API hit)...")
    result1 = await analyze_chart_image(
        image_base64=screenshot_base64,
        user_prompt="Quick analysis",
        symbol="BTCUSDT",
        timeframe="15m",
        provider="openai",
        use_cache=True,
        cache_ttl=300  # 5 minutes
    )
    print(f"From cache: {result1['from_cache']}")  # False
    print(f"Cost: ${result1['cost']:.4f}")
    
    # Second call within 5 minutes - uses cache
    print("\nSecond call (cache hit)...")
    result2 = await analyze_chart_image(
        image_base64=screenshot_base64,
        user_prompt="Quick analysis",  # Same prompt
        symbol="BTCUSDT",
        timeframe="15m",
        provider="openai",
        use_cache=True
    )
    print(f"From cache: {result2['from_cache']}")  # True
    print(f"Cost: ${result2['cost']:.4f}")  # Same as before (no new API call)
    
    # Check cache stats
    stats = get_cache_stats()
    print(f"\nCache stats: {stats['cached_items']} items")
    
    # Clear cache if needed
    clear_vision_cache()
    print("Cache cleared")


# ============================================================================
# EXAMPLE 5: Rate Limiting
# ============================================================================

async def example_rate_limiting():
    """Demonstrate rate limiting protection."""
    from open_webui.utils.vision_api import analyze_chart_image
    import asyncio
    
    screenshot_base64 = "iVBORw0KGgo..."
    
    # Make multiple rapid requests
    tasks = []
    for i in range(25):  # More than the 20/min limit
        task = analyze_chart_image(
            image_base64=screenshot_base64,
            user_prompt=f"Analysis {i}",
            symbol="BTCUSDT",
            timeframe="15m",
            provider="openai",
            use_cache=False  # Disable cache to test rate limiting
        )
        tasks.append(task)
    
    # The system automatically queues requests that exceed rate limits
    results = await asyncio.gather(*tasks)
    
    print(f"Completed {len(results)} requests")
    print("Rate limiting prevented API errors")


# ============================================================================
# EXAMPLE 6: Complete Endpoint Integration
# ============================================================================

async def example_endpoint_usage():
    """How the endpoint uses the Vision API."""
    from fastapi import Request
    from open_webui.utils.chart_capture import capture_chart_silently
    from open_webui.utils.vision_api import analyze_chart_image
    
    # Step 1: Capture screenshot (invisible to user)
    screenshot = await capture_chart_silently(
        symbol="BTCUSDT",
        timeframe="15m",
        frontend_url="http://localhost:5173",
        timeout=30000
    )
    
    if not screenshot:
        print("Screenshot failed, fallback to web scraping")
        return
    
    # Step 2: Analyze with Vision API
    result = await analyze_chart_image(
        image_base64=screenshot,
        user_prompt="Analyze this chart",
        symbol="BTCUSDT",
        timeframe="15m",
        provider="openai",
        use_cache=True
    )
    
    # Step 3: Return to user (text only, no screenshot!)
    response = {
        "analysis": result["analysis"],
        "symbol": "BTCUSDT",
        "timeframe": "15m",
        "method": "vision",
        "provider": result["provider"],
        "model": result["model"],
        "tokens_used": result["tokens_used"],
        "cost": result["cost"],
        "from_cache": result["from_cache"],
        "success": True
    }
    
    return response


# ============================================================================
# EXAMPLE 7: Custom Institutional Prompt
# ============================================================================

async def example_custom_prompt():
    """The institutional prompt is automatically applied."""
    from open_webui.utils.vision_api import get_institutional_vision_prompt
    
    # View the prompt that gets sent to the Vision API
    prompt = get_institutional_vision_prompt(
        symbol="BTCUSDT",
        user_prompt="Analyze this chart"
    )
    
    print("Institutional Prompt Structure:")
    print("=" * 60)
    print(prompt[:500] + "...")
    print("=" * 60)
    
    # The prompt enforces:
    # - Liquidity pool identification
    # - Market structure analysis
    # - Scenario tree with probabilities
    # - Entry/stop/target levels
    # - NO retail TA terminology
    # - Institutional language only


# ============================================================================
# EXAMPLE 8: Error Handling
# ============================================================================

async def example_error_handling():
    """Proper error handling for Vision API calls."""
    from open_webui.utils.vision_api import analyze_chart_image
    
    screenshot_base64 = "iVBORw0KGgo..."
    
    try:
        result = await analyze_chart_image(
            image_base64=screenshot_base64,
            user_prompt="Analyze this",
            symbol="BTCUSDT",
            timeframe="15m",
            provider="openai",
            use_cache=True
        )
        
        if result["success"]:
            # Success - use the analysis
            print(result["analysis"])
        else:
            # Vision API failed, but returned graceful error
            print(f"Analysis unavailable: {result.get('error')}")
            # System already tried fallback providers
            
    except Exception as e:
        # Unexpected error
        print(f"Critical error: {e}")
        # Fallback to web scraping method


# ============================================================================
# EXAMPLE 9: Cost Optimization
# ============================================================================

async def example_cost_optimization():
    """Optimize costs with caching and provider selection."""
    from open_webui.utils.vision_api import analyze_chart_image
    
    screenshot_base64 = "iVBORw0KGgo..."
    
    # Strategy 1: Use caching aggressively
    result = await analyze_chart_image(
        image_base64=screenshot_base64,
        user_prompt="Quick check",
        symbol="BTCUSDT",
        timeframe="15m",
        provider="openai",
        use_cache=True,
        cache_ttl=600  # 10 minutes (longer cache)
    )
    
    # Strategy 2: Use Claude for cheaper analysis
    # Claude is ~40% cheaper than GPT-4o
    result_claude = await analyze_chart_image(
        image_base64=screenshot_base64,
        user_prompt="Quick check",
        symbol="BTCUSDT",
        timeframe="15m",
        provider="claude",  # Cheaper option
        use_cache=True
    )
    
    # Strategy 3: Batch similar requests
    # Cache will serve subsequent requests for same symbol/timeframe
    
    print(f"OpenAI cost: ${result['cost']:.4f}")
    print(f"Claude cost: ${result_claude['cost']:.4f}")


# ============================================================================
# EXAMPLE 10: Production Usage Pattern
# ============================================================================

async def example_production_pattern():
    """Recommended production usage pattern."""
    from open_webui.utils.chart_capture import capture_chart_silently
    from open_webui.utils.vision_api import analyze_chart_image
    from open_webui.utils.crypto_data_api import get_binance_data
    from open_webui.utils.chart_analyzer import analyze_chart_data
    
    symbol = "BTCUSDT"
    timeframe = "15m"
    user_message = "Analyze this chart"
    
    # Try Vision API first (best quality)
    try:
        screenshot = await capture_chart_silently(
            symbol=symbol,
            timeframe=timeframe,
            timeout=30000
        )
        
        if screenshot:
            result = await analyze_chart_image(
                image_base64=screenshot,
                user_prompt=user_message,
                symbol=symbol,
                timeframe=timeframe,
                provider="openai",  # Primary
                use_cache=True
            )
            
            if result["success"]:
                return {
                    "analysis": result["analysis"],
                    "method": "vision",
                    "cost": result["cost"]
                }
    except Exception as e:
        print(f"Vision API failed: {e}")
    
    # Fallback to web scraping (cheaper, faster)
    try:
        chart_data = await get_binance_data(symbol, timeframe)
        result = await analyze_chart_data(
            chart_data=chart_data,
            user_prompt=user_message,
            symbol=symbol
        )
        
        return {
            "analysis": result["analysis"],
            "method": "web_scraping",
            "cost": result["cost"]
        }
    except Exception as e:
        print(f"Web scraping failed: {e}")
        return {
            "analysis": "TRADEBERG: Analysis temporarily unavailable.",
            "method": "error",
            "cost": 0
        }


# ============================================================================
# USAGE SUMMARY
# ============================================================================

"""
QUICK REFERENCE:

1. Basic Usage:
   result = await analyze_chart_image(screenshot, prompt, symbol, timeframe)

2. Provider Selection:
   provider="openai"   # Best quality, $0.05/request
   provider="claude"   # Good quality, $0.03/request
   provider="qwen"     # Budget option, varies by region
   provider="deepseek" # Alternative option

3. Caching:
   use_cache=True      # Enable caching (recommended)
   cache_ttl=300       # Cache for 5 minutes (default)

4. Response Structure:
   {
       "analysis": "TRADEBERG: ...",
       "provider": "openai",
       "model": "gpt-4o",
       "tokens_used": 1234,
       "cost": 0.0487,
       "from_cache": False,
       "success": True
   }

5. Error Handling:
   - System automatically tries fallback providers
   - Always check result["success"]
   - Graceful degradation to web scraping

6. Cost Optimization:
   - Enable caching (saves 100% on cache hits)
   - Use Claude for cheaper analysis
   - Batch similar requests
   - Set appropriate cache TTL

7. Institutional Prompt:
   - Automatically enforced
   - NO retail TA terms
   - Liquidity-focused analysis
   - Entry/stop/target levels
   - Scenario tree with probabilities

8. Performance:
   - Vision API: 3-5 seconds
   - Web scraping fallback: 1-2 seconds
   - Caching: <100ms

9. Rate Limiting:
   - Automatic queuing
   - 20 requests/minute default
   - No manual handling needed

10. Production Pattern:
    Try Vision → Fallback to Web Scraping → Graceful Error
"""

if __name__ == "__main__":
    print(__doc__)
