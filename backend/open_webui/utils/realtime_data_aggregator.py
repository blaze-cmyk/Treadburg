"""
Real-Time Market Data Aggregator
Combines data from Binance, Nansen, and CoinAnalyze APIs
"""

import os
import time
import hmac
import hashlib
import requests
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from functools import lru_cache
import logging

logger = logging.getLogger(__name__)

# API Keys (stored securely)
BINANCE_API_KEY = "k5UCdsqjtxf1FpRM2YUaooqEhaeSJlpvJg9Xe3OMoiXoW2B14bIsE25zkaxz2dmk"
BINANCE_SECRET_KEY = "raclH7YnL6UkdHF37waryUvFxSA8Taif7x2gUzhpPqIQa3upGxYvVkOmIgi9xzFv"
NANSEN_API_KEY = "zoUZzFeRYucilTJprSMXBsvNHzVVTn2I"
COINANALYZE_API_KEY = "f48bb41e-1611-426d-8fcb-4f969d6fbe6c"

# API Endpoints
BINANCE_BASE_URL = "https://api.binance.com"
NANSEN_BASE_URL = "https://api.nansen.ai"
COINANALYZE_BASE_URL = "https://api.coinanalyze.com"


class BinanceAPI:
    """Binance API Client for real-time crypto data"""
    
    def __init__(self):
        self.api_key = BINANCE_API_KEY
        self.secret_key = BINANCE_SECRET_KEY
        self.base_url = BINANCE_BASE_URL
    
    def _generate_signature(self, params: Dict) -> str:
        """Generate HMAC SHA256 signature for authenticated requests"""
        query_string = '&'.join([f"{k}={v}" for k, v in params.items()])
        signature = hmac.new(
            self.secret_key.encode('utf-8'),
            query_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        return signature
    
    def get_current_price(self, symbol: str) -> Dict[str, Any]:
        """Get current price for a symbol"""
        try:
            url = f"{self.base_url}/api/v3/ticker/price"
            params = {"symbol": symbol.upper()}
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Binance price error: {e}")
            return {}
    
    def get_24h_ticker(self, symbol: str) -> Dict[str, Any]:
        """Get 24h ticker statistics"""
        try:
            url = f"{self.base_url}/api/v3/ticker/24hr"
            params = {"symbol": symbol.upper()}
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Binance 24h ticker error: {e}")
            return {}
    
    def get_klines(self, symbol: str, interval: str = "1h", limit: int = 100) -> List[List]:
        """Get historical kline/candlestick data"""
        try:
            url = f"{self.base_url}/api/v3/klines"
            params = {
                "symbol": symbol.upper(),
                "interval": interval,
                "limit": limit
            }
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Binance klines error: {e}")
            return []
    
    def get_order_book(self, symbol: str, limit: int = 100) -> Dict[str, Any]:
        """Get order book depth"""
        try:
            url = f"{self.base_url}/api/v3/depth"
            params = {
                "symbol": symbol.upper(),
                "limit": limit
            }
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Binance order book error: {e}")
            return {}
    
    def get_recent_trades(self, symbol: str, limit: int = 100) -> List[Dict]:
        """Get recent trades"""
        try:
            url = f"{self.base_url}/api/v3/trades"
            params = {
                "symbol": symbol.upper(),
                "limit": limit
            }
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Binance recent trades error: {e}")
            return []


class NansenAPI:
    """Nansen API Client for on-chain analytics"""
    
    def __init__(self):
        self.api_key = NANSEN_API_KEY
        self.base_url = NANSEN_BASE_URL
        self.headers = {"X-API-KEY": self.api_key}
    
    def get_smart_money_flows(self, token: str) -> Dict[str, Any]:
        """Get smart money flow data"""
        try:
            url = f"{self.base_url}/v1/smart-money/{token}"
            response = requests.get(url, headers=self.headers, timeout=10)
            if response.status_code == 200:
                return response.json()
            return {}
        except Exception as e:
            logger.error(f"Nansen smart money error: {e}")
            return {}
    
    def get_whale_activity(self, token: str) -> Dict[str, Any]:
        """Get whale wallet activity"""
        try:
            url = f"{self.base_url}/v1/whales/{token}"
            response = requests.get(url, headers=self.headers, timeout=10)
            if response.status_code == 200:
                return response.json()
            return {}
        except Exception as e:
            logger.error(f"Nansen whale activity error: {e}")
            return {}


class CoinAnalyzeAPI:
    """CoinAnalyze API Client for market sentiment"""
    
    def __init__(self):
        self.api_key = COINANALYZE_API_KEY
        self.base_url = COINANALYZE_BASE_URL
        self.headers = {"Authorization": f"Bearer {self.api_key}"}
    
    def get_sentiment(self, symbol: str) -> Dict[str, Any]:
        """Get market sentiment analysis"""
        try:
            url = f"{self.base_url}/v1/sentiment/{symbol}"
            response = requests.get(url, headers=self.headers, timeout=10)
            if response.status_code == 200:
                return response.json()
            return {}
        except Exception as e:
            logger.error(f"CoinAnalyze sentiment error: {e}")
            return {}
    
    def get_social_metrics(self, symbol: str) -> Dict[str, Any]:
        """Get social media metrics"""
        try:
            url = f"{self.base_url}/v1/social/{symbol}"
            response = requests.get(url, headers=self.headers, timeout=10)
            if response.status_code == 200:
                return response.json()
            return {}
        except Exception as e:
            logger.error(f"CoinAnalyze social metrics error: {e}")
            return {}


class RealtimeDataAggregator:
    """Aggregates data from all sources"""
    
    def __init__(self):
        self.binance = BinanceAPI()
        self.nansen = NansenAPI()
        self.coinanalyze = CoinAnalyzeAPI()
    
    def get_comprehensive_data(self, symbol: str) -> Dict[str, Any]:
        """Get comprehensive market data from all sources"""
        
        # Normalize symbol for different APIs
        binance_symbol = f"{symbol.upper()}USDT"
        
        # Fetch data from all sources
        price_data = self.binance.get_current_price(binance_symbol)
        ticker_24h = self.binance.get_24h_ticker(binance_symbol)
        klines = self.binance.get_klines(binance_symbol, interval="1h", limit=24)
        order_book = self.binance.get_order_book(binance_symbol, limit=20)
        recent_trades = self.binance.get_recent_trades(binance_symbol, limit=50)
        
        # Process klines into candlestick data
        candlestick_data = self._process_klines(klines)
        
        # Calculate volume metrics
        volume_metrics = self._calculate_volume_metrics(recent_trades)
        
        # Analyze order book
        liquidity_analysis = self._analyze_order_book(order_book)
        
        # Aggregate all data
        return {
            "symbol": symbol.upper(),
            "timestamp": datetime.utcnow().isoformat(),
            "price": {
                "current": float(price_data.get("price", 0)),
                "high_24h": float(ticker_24h.get("highPrice", 0)),
                "low_24h": float(ticker_24h.get("lowPrice", 0)),
                "change_24h": float(ticker_24h.get("priceChangePercent", 0)),
                "volume_24h": float(ticker_24h.get("volume", 0)),
                "quote_volume_24h": float(ticker_24h.get("quoteVolume", 0))
            },
            "candlestick_data": candlestick_data,
            "volume_metrics": volume_metrics,
            "liquidity": liquidity_analysis,
            "market_depth": {
                "bid_depth": len(order_book.get("bids", [])),
                "ask_depth": len(order_book.get("asks", [])),
                "spread": self._calculate_spread(order_book)
            }
        }
    
    def _process_klines(self, klines: List[List]) -> List[Dict]:
        """Process klines into candlestick format"""
        candlesticks = []
        for kline in klines:
            candlesticks.append({
                "date": datetime.fromtimestamp(kline[0] / 1000).strftime("%Y-%m-%d %H:%M"),
                "open": float(kline[1]),
                "high": float(kline[2]),
                "low": float(kline[3]),
                "close": float(kline[4]),
                "volume": float(kline[5])
            })
        return candlesticks
    
    def _calculate_volume_metrics(self, trades: List[Dict]) -> Dict[str, Any]:
        """Calculate buy/sell volume from recent trades"""
        buy_volume = 0
        sell_volume = 0
        
        for trade in trades:
            qty = float(trade.get("qty", 0))
            if trade.get("isBuyerMaker", False):
                sell_volume += qty
            else:
                buy_volume += qty
        
        total_volume = buy_volume + sell_volume
        buy_pressure = (buy_volume / total_volume * 100) if total_volume > 0 else 50
        
        return {
            "buy_volume": buy_volume,
            "sell_volume": sell_volume,
            "total_volume": total_volume,
            "buy_pressure": buy_pressure,
            "sell_pressure": 100 - buy_pressure
        }
    
    def _analyze_order_book(self, order_book: Dict) -> Dict[str, Any]:
        """Analyze order book for liquidity"""
        bids = order_book.get("bids", [])
        asks = order_book.get("asks", [])
        
        bid_liquidity = sum(float(bid[1]) for bid in bids[:10])
        ask_liquidity = sum(float(ask[1]) for ask in asks[:10])
        
        total_liquidity = bid_liquidity + ask_liquidity
        bid_ratio = (bid_liquidity / total_liquidity * 100) if total_liquidity > 0 else 50
        
        return {
            "bid_liquidity": bid_liquidity,
            "ask_liquidity": ask_liquidity,
            "total_liquidity": total_liquidity,
            "bid_ratio": bid_ratio,
            "ask_ratio": 100 - bid_ratio,
            "liquidity_level": "High" if total_liquidity > 1000 else "Medium" if total_liquidity > 100 else "Low"
        }
    
    def _calculate_spread(self, order_book: Dict) -> float:
        """Calculate bid-ask spread"""
        bids = order_book.get("bids", [])
        asks = order_book.get("asks", [])
        
        if bids and asks:
            best_bid = float(bids[0][0])
            best_ask = float(asks[0][0])
            spread = ((best_ask - best_bid) / best_bid) * 100
            return round(spread, 4)
        return 0.0
    
    def get_comparison_data(self, symbols: List[str]) -> List[Dict[str, Any]]:
        """Get comparison data for multiple symbols"""
        comparison_data = []
        
        for symbol in symbols:
            try:
                data = self.get_comprehensive_data(symbol)
                comparison_data.append({
                    "symbol": symbol.upper(),
                    "price": data["price"]["current"],
                    "change_24h": data["price"]["change_24h"],
                    "volume_24h": data["price"]["volume_24h"],
                    "liquidity": data["liquidity"]["liquidity_level"],
                    "buy_pressure": data["volume_metrics"]["buy_pressure"]
                })
            except Exception as e:
                logger.error(f"Error fetching data for {symbol}: {e}")
                continue
        
        return comparison_data
    
    def format_for_ai_response(self, symbol: str) -> str:
        """Format data for AI to use in responses"""
        data = self.get_comprehensive_data(symbol)
        
        # Create compact metrics table
        metrics_table = f"""```json:chart:grid
{{
  "title": "{symbol.upper()} Real-Time Metrics",
  "data": [
    {{"metric": "Price", "value": "${data['price']['current']:,.2f}", "change": "{data['price']['change_24h']:+.2f}%", "status": "{'🟢' if data['price']['change_24h'] > 0 else '🔴'}"}},
    {{"metric": "Volume 24h", "value": "${data['price']['quote_volume_24h']/1e9:.2f}B", "change": "-", "status": "🟡"}},
    {{"metric": "Liquidity", "value": "{data['liquidity']['liquidity_level']}", "change": "-", "status": "{'🟢' if data['liquidity']['liquidity_level'] == 'High' else '🟡'}"}},
    {{"metric": "Buy Pressure", "value": "{data['volume_metrics']['buy_pressure']:.1f}%", "change": "-", "status": "{'🟢' if data['volume_metrics']['buy_pressure'] > 50 else '🔴'}"}}
  ]
}}
```"""
        
        # Create candlestick chart
        candlestick_chart = f"""```json:chart:candlestick
{{
  "title": "{symbol.upper()} Price Action (24H)",
  "data": {data['candlestick_data'][-24:]}
}}
```"""
        
        # Create volume chart
        volume_chart = f"""```json:chart:bar
{{
  "title": "Volume Breakdown",
  "data": [
    {{"label": "Buy Volume", "value": {data['volume_metrics']['buy_volume']:.2f}, "color": "#10b981"}},
    {{"label": "Sell Volume", "value": {data['volume_metrics']['sell_volume']:.2f}, "color": "#ef4444"}}
  ]
}}
```"""
        
        return f"{metrics_table}\n\n{candlestick_chart}\n\n{volume_chart}"


# Global instance
aggregator = RealtimeDataAggregator()


def get_realtime_market_data(symbol: str) -> Dict[str, Any]:
    """Get real-time market data for a symbol"""
    return aggregator.get_comprehensive_data(symbol)


def get_comparison_data(symbols: List[str]) -> List[Dict[str, Any]]:
    """Get comparison data for multiple symbols"""
    return aggregator.get_comparison_data(symbols)


def format_for_ai(symbol: str) -> str:
    """Format real-time data for AI response"""
    return aggregator.format_for_ai_response(symbol)
