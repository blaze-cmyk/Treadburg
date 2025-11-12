"""
Chart Data Analyzer
Analyzes scraped trading data using GPT-4 (text-only, no Vision API needed!)
Much faster, cheaper, and more accurate than screenshot + Vision
"""

import os
from typing import Dict, Any, List
from openai import OpenAI

from open_webui.utils import logger
from open_webui.utils.crypto_data_api import format_volume

log = logger.logger


def get_openai_client() -> OpenAI:
    """Get OpenAI client instance."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable not set")
    return OpenAI(api_key=api_key)


async def analyze_chart_data(
    chart_data: Dict[str, Any],
    user_prompt: str,
    symbol: str = "BTCUSDT"
) -> Dict[str, Any]:
    """
    Analyze chart data using text-only GPT-4.
    NO VISION API NEEDED - saves money and is faster!
    
    Args:
        chart_data: Dict with price data, candles, and indicators
        user_prompt: Original user message/prompt
        symbol: Trading symbol being analyzed
        
    Returns:
        Dict with analysis text and metadata
    """
    try:
        log.info(f"🧠 Analyzing chart data with GPT-4 (text-only) for {symbol}...")
        
        client = get_openai_client()
        
        # Format data as structured text
        data_formatted = format_chart_data(chart_data)
        
        system_prompt = """You are TRADEBERG — an institutional AI terminal. You reason like a macro/quant/market‑microstructure desk combined.

CRITICAL RULES:
1. NEVER mention "screenshot", "image", "scraped data", "API", or ask for any charts/images
2. Market data has been automatically fetched - use it directly
3. Speak as if you're directly observing live market data
4. Be concise and actionable - traders need quick insights
5. Focus on: trend direction, key levels, liquidity zones, volume, microstructure
6. Always include: current bias (net long/short positioning), entry zones, stop (invalid liquidity), targets (liquidity sweeps)
7. Use institutional language: sweep, absorption, imbalance, trapped liquidity, risk unwind, vol compression, deleveraging, re‑risking, basis, carry, gamma/vega dynamics

NEVER ask for screenshots or images - the data is already provided in the context above.

Format your response using institutional trading framework:
TRADEBERG: [Brief liquidity-first overview]

[Quick read]
Liquidity Map: [External pools, internal magnets, session extremes]

Path Likelihood: [Scenario probabilities with beneficiaries/victims]

Triggers/Invalidations: [Acceptance/rejection criteria]

Tradeable Set-ups: [Entry zones, stops, targets, rationale]

Risk: [Position sizing, invalidation criteria]

Use institutional language throughout."""
        
        response = client.chat.completions.create(
            model="gpt-4-turbo-preview",  # Text-only, cheaper than vision!
            max_tokens=1000,
            temperature=0.7,
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": f"{data_formatted}\n\nUser Question: {user_prompt}"
                }
            ]
        )
        
        analysis = response.choices[0].message.content
        
        tokens_used = response.usage.total_tokens if response.usage else 0
        cost = tokens_used * 0.00001  # ~$0.01 per 1k tokens (much cheaper than vision!)
        
        log.info(f"✅ Analysis complete - Cost: ${cost:.4f} (vs $0.05+ for vision)")
        
        return {
            "analysis": analysis,
            "raw_data": chart_data,
            "tokens_used": tokens_used,
            "cost": round(cost, 4),
            "symbol": symbol,
            "used_analysis": True,
            "method": "web_scraping"  # vs "screenshot"
        }
        
    except Exception as error:
        log.error(f"❌ Analysis failed: {error}")
        
        # Fallback response
        return {
            "analysis": f"TRADEBERG: Unable to analyze {symbol} right now due to a technical issue. Please try again.",
            "error": True,
            "used_analysis": False
        }


def format_chart_data(chart_data: Dict[str, Any]) -> str:
    """Format chart data as structured text for GPT analysis."""
    symbol = chart_data.get("symbol", "N/A")
    price = chart_data.get("current_price", 0)
    change_24h = chart_data.get("change_24h", 0)
    high_24h = chart_data.get("high_24h", 0)
    low_24h = chart_data.get("low_24h", 0)
    volume_24h = chart_data.get("volume_24h", 0)
    indicators = chart_data.get("indicators", {})
    candles = chart_data.get("candles", [])
    
    formatted = f"""
# Trading Data for {symbol}

## Current Market Stats
- Price: ${price:,.2f}
- 24h Change: {change_24h:.2f}%
- 24h High: ${high_24h:,.2f}
- 24h Low: ${low_24h:,.2f}
- 24h Volume: {format_volume(volume_24h)}

## Technical Indicators
{format_indicators(indicators)}

## Recent Price Action (Last 5 Candles)
{format_candles(candles[-5:])}

## Market Trend
Overall Trend: {indicators.get('trend', 'NEUTRAL')}
Support Level: ${indicators.get('support_resistance', {}).get('support', 'N/A')}
Resistance Level: ${indicators.get('support_resistance', {}).get('resistance', 'N/A')}
"""
    return formatted


def format_indicators(indicators: Dict[str, Any]) -> str:
    """Format indicators for display."""
    rsi = indicators.get("rsi", "N/A")
    rsi_signal = get_rsi_signal(rsi) if isinstance(rsi, (int, float)) else ""
    
    sma20 = indicators.get("sma20", "N/A")
    ema20 = indicators.get("ema20", "N/A")
    bb = indicators.get("bollinger_bands", {})
    
    return f"""
- RSI(14): {rsi} {rsi_signal}
- SMA(20): ${sma20}
- EMA(20): ${ema20}
- Bollinger Bands:
  - Upper: ${bb.get('upper', 'N/A')}
  - Middle: ${bb.get('middle', 'N/A')}
  - Lower: ${bb.get('lower', 'N/A')}
"""
    
def format_candles(candles: List[Dict[str, Any]]) -> str:
    """Format candles for display."""
    if not candles:
        return "No candle data available"
    
    lines = []
    for i, candle in enumerate(candles[-5:], 1):
        lines.append(
            f"Candle {i}: Open ${candle['open']:,.2f}, "
            f"High ${candle['high']:,.2f}, "
            f"Low ${candle['low']:,.2f}, "
            f"Close ${candle['close']:,.2f}, "
            f"Volume {format_volume(candle['volume'])}"
        )
    
    return "\n".join(lines)


def format_volume(volume: float) -> str:
    """Format volume for display."""
    if volume >= 1e9:
        return f"${volume / 1e9:.2f}B"
    elif volume >= 1e6:
        return f"${volume / 1e6:.2f}M"
    elif volume >= 1e3:
        return f"${volume / 1e3:.2f}K"
    return f"${volume:,.2f}"


def get_rsi_signal(rsi: float) -> str:
    """Get RSI signal indicator."""
    if rsi > 70:
        return "🔴 OVERBOUGHT"
    elif rsi < 30:
        return "🟢 OVERSOLD"
    return "🟡 NEUTRAL"

