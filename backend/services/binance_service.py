"""
Binance API service for real-time cryptocurrency prices
"""
import aiohttp
import logging
from typing import Dict, Optional, List
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class BinanceService:
    """Service for fetching real-time crypto prices from Binance"""
    
    BASE_URL = "https://api.binance.com/api/v3"
    
    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session"""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session
    
    async def get_price(self, symbol: str) -> Dict:
        """
        Get current price for a symbol
        Example: BTC, ETH, SOL -> returns BTCUSDT, ETHUSDT, SOLUSDT price
        """
        try:
            # Normalize symbol (add USDT if not present)
            if not symbol.endswith('USDT'):
                symbol = f"{symbol.upper()}USDT"
            
            session = await self._get_session()
            
            # Get 24hr ticker data
            url = f"{self.BASE_URL}/ticker/24hr"
            params = {"symbol": symbol}
            
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    return {
                        "symbol": symbol,
                        "price": float(data["lastPrice"]),
                        "change_24h": float(data["priceChange"]),
                        "change_percent_24h": float(data["priceChangePercent"]),
                        "high_24h": float(data["highPrice"]),
                        "low_24h": float(data["lowPrice"]),
                        "volume_24h": float(data["volume"]),
                        "timestamp": datetime.now().isoformat()
                    }
                else:
                    logger.error(f"Binance API error: {response.status}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error fetching price from Binance: {e}")
            return None
    
    async def get_multiple_prices(self, symbols: List[str]) -> Dict[str, Dict]:
        """Get prices for multiple symbols"""
        results = {}
        for symbol in symbols:
            price_data = await self.get_price(symbol)
            if price_data:
                results[symbol] = price_data
        return results
    
    async def get_klines(self, symbol: str, interval: str = "1h", limit: int = 24) -> List[Dict]:
        """
        Get candlestick data for charts
        Intervals: 1m, 5m, 15m, 1h, 4h, 1d, 1w
        """
        try:
            # Normalize symbol
            if not symbol.endswith('USDT'):
                symbol = f"{symbol.upper()}USDT"
            
            session = await self._get_session()
            
            url = f"{self.BASE_URL}/klines"
            params = {
                "symbol": symbol,
                "interval": interval,
                "limit": limit
            }
            
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Format candlestick data
                    klines = []
                    for candle in data:
                        klines.append({
                            "timestamp": datetime.fromtimestamp(candle[0] / 1000).isoformat(),
                            "open": float(candle[1]),
                            "high": float(candle[2]),
                            "low": float(candle[3]),
                            "close": float(candle[4]),
                            "volume": float(candle[5])
                        })
                    
                    return klines
                else:
                    logger.error(f"Binance klines API error: {response.status}")
                    return []
                    
        except Exception as e:
            logger.error(f"Error fetching klines from Binance: {e}")
            return []
    
    async def get_order_book(self, symbol: str, limit: int = 10) -> Dict:
        """Get order book (bid/ask) data"""
        try:
            # Normalize symbol
            if not symbol.endswith('USDT'):
                symbol = f"{symbol.upper()}USDT"
            
            session = await self._get_session()
            
            url = f"{self.BASE_URL}/depth"
            params = {
                "symbol": symbol,
                "limit": limit
            }
            
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    return {
                        "symbol": symbol,
                        "bids": [[float(price), float(qty)] for price, qty in data["bids"][:limit]],
                        "asks": [[float(price), float(qty)] for price, qty in data["asks"][:limit]],
                        "timestamp": datetime.now().isoformat()
                    }
                else:
                    logger.error(f"Binance order book API error: {response.status}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error fetching order book from Binance: {e}")
            return None
    
    async def close(self):
        """Close the aiohttp session"""
        if self.session and not self.session.closed:
            await self.session.close()

# Global instance
binance_service = BinanceService()
