"""
Crypto Data API Service
Fetches real-time trading data from Binance/CoinGecko APIs
MUCH faster and more reliable than screenshot + Vision API
"""

import aiohttp
import asyncio
from typing import Dict, Any, List, Optional
from open_webui.utils import logger

log = logger.logger


async def get_binance_data(symbol: str = "BTCUSDT", interval: str = "1h") -> Dict[str, Any]:
    """
    Get crypto data from Binance API.
    This is MUCH faster and more reliable than scraping screenshots!
    
    Args:
        symbol: Trading symbol (e.g., "BTCUSDT", "ETHUSDT")
        interval: Timeframe (1m, 5m, 15m, 1h, 4h, 1d)
        
    Returns:
        Dict with price data, candles, and indicators
    """
    try:
        log.info(f"📊 Fetching data from Binance for {symbol} @ {interval}...")
        
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
            # Get 24h ticker data
            ticker_url = "https://api.binance.com/api/v3/ticker/24hr"
            try:
                async with session.get(ticker_url, params={"symbol": symbol}) as resp:
                    if resp.status != 200:
                        error_text = await resp.text()
                        raise Exception(f"Binance API error: {resp.status} - {error_text}")
                    ticker = await resp.json()
                    log.info(f"✅ Ticker data received for {symbol}")
            except Exception as e:
                log.error(f"❌ Ticker fetch failed: {e}")
                raise
            
            # Get recent candles
            klines_url = "https://api.binance.com/api/v3/klines"
            try:
                async with session.get(
                    klines_url,
                    params={
                        "symbol": symbol,
                        "interval": interval,
                        "limit": 100
                    }
                ) as resp:
                    if resp.status != 200:
                        error_text = await resp.text()
                        raise Exception(f"Binance klines error: {resp.status} - {error_text}")
                    klines_data = await resp.json()
                    log.info(f"✅ Klines data received: {len(klines_data)} candles")
            except Exception as e:
                log.error(f"❌ Klines fetch failed: {e}")
                raise
        
        # Parse candles
        candles = []
        for candle in klines_data:
            candles.append({
                "timestamp": candle[0],
                "open": float(candle[1]),
                "high": float(candle[2]),
                "low": float(candle[3]),
                "close": float(candle[4]),
                "volume": float(candle[5])
            })
        
        # Calculate technical indicators
        indicators = calculate_indicators(candles)
        
        result = {
            "symbol": symbol,
            "current_price": float(ticker["lastPrice"]),
            "change_24h": float(ticker["priceChangePercent"]),
            "high_24h": float(ticker["highPrice"]),
            "low_24h": float(ticker["lowPrice"]),
            "volume_24h": float(ticker["volume"]),
            "candles": candles[-20:],  # Last 20 candles
            "indicators": indicators
        }
        
        log.info(f"✅ Binance data fetched: {symbol} at ${result['current_price']}")
        return result
        
    except Exception as error:
        log.error(f"❌ Binance API error: {error}")
        raise


def calculate_indicators(candles: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Calculate technical indicators from candle data.
    
    Args:
        candles: List of candle dicts with OHLCV data
        
    Returns:
        Dict with calculated indicators
    """
    if not candles or len(candles) < 20:
        return {
            "rsi": "N/A",
            "sma20": "N/A",
            "ema20": "N/A",
            "bollinger_bands": {"upper": "N/A", "middle": "N/A", "lower": "N/A"},
            "trend": "NEUTRAL",
            "support_resistance": {"support": "N/A", "resistance": "N/A"}
        }
    
    closes = [c["close"] for c in candles]
    highs = [c["high"] for c in candles]
    lows = [c["low"] for c in candles]
    
    return {
        "rsi": calculate_rsi(closes, 14),
        "sma20": calculate_sma(closes, 20),
        "ema20": calculate_ema(closes, 20),
        "bollinger_bands": calculate_bollinger(closes, 20),
        "trend": determine_trend(closes),
        "support_resistance": find_support_resistance(highs, lows)
    }


def calculate_rsi(prices: List[float], period: int = 14) -> float:
    """Calculate RSI (Relative Strength Index)."""
    if len(prices) < period + 1:
        return 50.0
    
    gains = []
    losses = []
    
    for i in range(len(prices) - period, len(prices)):
        change = prices[i] - prices[i - 1]
        if change > 0:
            gains.append(change)
            losses.append(0.0)
        else:
            gains.append(0.0)
            losses.append(abs(change))
    
    avg_gain = sum(gains) / period
    avg_loss = sum(losses) / period
    
    if avg_loss == 0:
        return 100.0
    
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    
    return round(rsi, 2)


def calculate_sma(prices: List[float], period: int) -> float:
    """Calculate Simple Moving Average."""
    if len(prices) < period:
        return prices[-1] if prices else 0.0
    
    slice_prices = prices[-period:]
    return round(sum(slice_prices) / period, 2)


def calculate_ema(prices: List[float], period: int) -> float:
    """Calculate Exponential Moving Average."""
    if len(prices) < period:
        return prices[-1] if prices else 0.0
    
    k = 2 / (period + 1)
    ema = prices[0]
    
    for price in prices[1:]:
        ema = (price * k) + (ema * (1 - k))
    
    return round(ema, 2)


def calculate_bollinger(prices: List[float], period: int) -> Dict[str, float]:
    """Calculate Bollinger Bands."""
    if len(prices) < period:
        sma = prices[-1] if prices else 0.0
        return {"upper": sma, "middle": sma, "lower": sma}
    
    sma = calculate_sma(prices, period)
    slice_prices = prices[-period:]
    
    # Calculate standard deviation
    squared_diffs = [(p - sma) ** 2 for p in slice_prices]
    variance = sum(squared_diffs) / period
    std_dev = variance ** 0.5
    
    return {
        "upper": round(sma + (2 * std_dev), 2),
        "middle": round(sma, 2),
        "lower": round(sma - (2 * std_dev), 2)
    }


def determine_trend(prices: List[float]) -> str:
    """Determine market trend from price action."""
    if len(prices) < 20:
        return "NEUTRAL"
    
    recent = prices[-10:]
    older = prices[-20:-10]
    
    recent_avg = sum(recent) / len(recent)
    older_avg = sum(older) / len(older)
    
    pct_change = ((recent_avg - older_avg) / older_avg) * 100
    
    if pct_change > 2:
        return "BULLISH"
    elif pct_change < -2:
        return "BEARISH"
    return "NEUTRAL"


def find_support_resistance(highs: List[float], lows: List[float]) -> Dict[str, float]:
    """Find support and resistance levels."""
    if not highs or not lows:
        return {"support": 0.0, "resistance": 0.0}
    
    recent_highs = highs[-20:] if len(highs) >= 20 else highs
    recent_lows = lows[-20:] if len(lows) >= 20 else lows
    
    return {
        "resistance": round(max(recent_highs), 2),
        "support": round(min(recent_lows), 2)
    }


async def get_coingecko_data(coin_id: str = "bitcoin") -> Dict[str, Any]:
    """
    Alternative: Get data from CoinGecko API (free, no auth needed).
    
    Args:
        coin_id: CoinGecko coin ID (e.g., "bitcoin", "ethereum")
        
    Returns:
        Dict with market data
    """
    try:
        log.info(f"📊 Fetching data from CoinGecko for {coin_id}...")
        
        async with aiohttp.ClientSession() as session:
            url = f"https://api.coingecko.com/api/v3/coins/{coin_id}"
            params = {
                "localization": "false",
                "tickers": "false",
                "community_data": "false",
                "developer_data": "false"
            }
            
            async with session.get(url, params=params) as resp:
                if resp.status != 200:
                    raise Exception(f"CoinGecko API error: {resp.status}")
                data = await resp.json()
        
        market_data = data.get("market_data", {})
        
        result = {
            "name": data.get("name", ""),
            "symbol": data.get("symbol", "").upper(),
            "current_price": market_data.get("current_price", {}).get("usd", 0),
            "change_24h": market_data.get("price_change_percentage_24h", 0),
            "high_24h": market_data.get("high_24h", {}).get("usd", 0),
            "low_24h": market_data.get("low_24h", {}).get("usd", 0),
            "market_cap": market_data.get("market_cap", {}).get("usd", 0),
            "volume_24h": market_data.get("total_volume", {}).get("usd", 0)
        }
        
        log.info(f"✅ CoinGecko data fetched: {result['symbol']} at ${result['current_price']}")
        return result
        
    except Exception as error:
        log.error(f"❌ CoinGecko API error: {error}")
        raise


def format_volume(volume: float) -> str:
    """Format volume for display."""
    if volume >= 1e9:
        return f"${volume / 1e9:.2f}B"
    elif volume >= 1e6:
        return f"${volume / 1e6:.2f}M"
    elif volume >= 1e3:
        return f"${volume / 1e3:.2f}K"
    return f"${volume:.2f}"

