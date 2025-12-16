import ccxt.async_support as ccxt
from config import settings
from typing import Dict, List, Optional, Union
import asyncio
from services.gemini_service import gemini_service
import re

class MarketDataService:
    def __init__(self):
        # Initialize CCXT (Binance global for better coverage)
        self.ccxt_exchange = ccxt.binance({
            'enableRateLimit': True,
        })
        print("✅ MarketDataService initialized (CCXT + Google Search Grounding)")

    async def close(self):
        await self.ccxt_exchange.close()

    def _is_crypto(self, ticker: str) -> bool:
        """Simple heuristic to detect crypto tickers"""
        ticker = ticker.upper()
        return "/" in ticker or ticker.endswith("USDT") or ticker.endswith("USD") or ticker in ["BTC", "ETH", "SOL", "DOGE"]

    async def get_snapshot(self, ticker: str) -> Dict:
        """
        Get a unified snapshot of market data.
        Returns: { symbol, price, volume, source, ... }
        """
        ticker = ticker.upper()
        
        if self._is_crypto(ticker):
            return await self._fetch_crypto_snapshot(ticker)
        else:
            return await self._fetch_stock_via_google(ticker)

    async def _fetch_crypto_snapshot(self, ticker: str) -> Dict:
        try:
            # Ensure format is like BTC/USDT
            if "/" not in ticker and not ticker.endswith("USDT"):
                symbol = f"{ticker}/USDT"
            else:
                symbol = ticker
                
            ticker_data = await self.ccxt_exchange.fetch_ticker(symbol)
            return {
                "symbol": symbol,
                "price": ticker_data.get('last'),
                "volume": ticker_data.get('quoteVolume'), # 24h volume in quote currency
                "change_24h": ticker_data.get('percentage'),
                "source": "CCXT (BinanceUS)"
            }
        except Exception as e:
            print(f"CCXT Error for {ticker}: {e}")
            return {"symbol": ticker, "error": str(e)}

    async def _fetch_stock_via_google(self, ticker: str) -> Dict:
        """
        Uses Gemini with Google Search tool to get live stock data.
        """
        prompt = f"What is the current price, 24h volume, and market cap of {ticker}? Return as JSON with keys: price, volume, market_cap, change_percent."
        
        try:
            response = await gemini_service.generate_content(
                prompt=prompt,
                use_search_grounding=True 
            )
            
            # Simple parsing of the response
            # In a real scenario, we'd want strict JSON output from Gemini
            # For now, we'll return the text and try to extract numbers if possible
            # or just pass the text to the agent context.
            
            return {
                "symbol": ticker,
                "raw_grounding_text": response,
                "source": "Google Search Grounding"
            }
        except Exception as e:
            print(f"Google Search Error for {ticker}: {e}")
            return {"symbol": ticker, "error": str(e)}

    async def get_price(self, ticker: str) -> Optional[float]:
        """Helper to get just price"""
        data = await self.get_snapshot(ticker)
        if "price" in data and data["price"]:
            return float(data["price"])
        # If google search, we might need to parse 'raw_grounding_text'
        # For now return None if not explicit
        return None

    async def get_market_snapshot(self, ticker: str) -> str:
        """Get a text summary of market data for the agent"""
        data = await self.get_snapshot(ticker)
        
        if "error" in data:
            return f"Market Data Error: {data['error']}"
            
        if data.get("source") == "Google Search Grounding":
            return f"GOOGLE SEARCH MARKET DATA ({ticker}):\n{data.get('raw_grounding_text')}"
            
        summary = f"CURRENT MARKET DATA ({data.get('symbol')}):\n"
        summary += f"Price: ${data.get('price', 0):,.2f}\n"
        summary += f"24h Change: {data.get('change_24h', 0)}%\n"
        summary += f"Volume: {data.get('volume', 'N/A')}\n"
        
        return summary

    # Keep historical data for crypto charts if needed, 
    # but for stocks we might rely on Vision or Search descriptions for now.
    async def get_historical_data(self, ticker: str, timeframe: str = '1d', limit: int = 100) -> Optional[List[Dict]]:
        if self._is_crypto(ticker):
            # ... (Existing CCXT logic) ...
             try:
                if "/" not in ticker and not ticker.endswith("USDT"):
                    symbol = f"{ticker}/USDT"
                else:
                    symbol = ticker
                
                tf_map = {'1d': '1d', '1h': '1h', '15m': '15m'}
                ccxt_tf = tf_map.get(timeframe, '1d')
                
                print(f"DEBUG: Fetching OHLCV for {symbol}...")
                ohlcv = await self.ccxt_exchange.fetch_ohlcv(symbol, timeframe=ccxt_tf, limit=limit)
                print(f"DEBUG: Fetched {len(ohlcv)} candles for {symbol}")
                return [
                    {
                        "timestamp": x[0], "open": x[1], "high": x[2], "low": x[3], "close": x[4], "volume": x[5]
                    }
                    for x in ohlcv
                ]
             except Exception as e:
                 print(f"CCXT Historical Error for {ticker}: {e}")
                 return None
        return None # No historicals for stocks via Google Search yet

market_data_service = MarketDataService()
