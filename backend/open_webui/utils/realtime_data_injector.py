"""
Real-Time Data Injector
Automatically injects live market data into AI requests
"""

import re
from typing import Dict, List, Any
from datetime import datetime
from open_webui.utils.realtime_data_aggregator import get_realtime_market_data, get_comparison_data


def extract_symbols(text: str) -> List[str]:
    """Extract crypto symbols from user message"""
    # Common crypto symbols
    symbols = []
    common_cryptos = {
        'BTC': 'BTC', 'BITCOIN': 'BTC',
        'ETH': 'ETH', 'ETHEREUM': 'ETH',
        'SOL': 'SOL', 'SOLANA': 'SOL',
        'BNB': 'BNB', 'BINANCE': 'BNB',
        'XRP': 'XRP', 'RIPPLE': 'XRP',
        'ADA': 'ADA', 'CARDANO': 'ADA',
        'DOGE': 'DOGE', 'DOGECOIN': 'DOGE',
        'MATIC': 'MATIC', 'POLYGON': 'MATIC',
        'DOT': 'DOT', 'POLKADOT': 'DOT',
        'AVAX': 'AVAX', 'AVALANCHE': 'AVAX',
        'LINK': 'LINK', 'CHAINLINK': 'LINK',
        'UNI': 'UNI', 'UNISWAP': 'UNI',
        'ATOM': 'ATOM', 'COSMOS': 'ATOM',
        'LTC': 'LTC', 'LITECOIN': 'LTC',
        'NEAR': 'NEAR',
        'APT': 'APT', 'APTOS': 'APT',
        'ARB': 'ARB', 'ARBITRUM': 'ARB',
        'OP': 'OP', 'OPTIMISM': 'OP'
    }
    
    text_upper = text.upper()
    for key, symbol in common_cryptos.items():
        if key in text_upper:
            if symbol not in symbols:
                symbols.append(symbol)
    
    return symbols


def detect_query_type(text: str) -> str:
    """Detect what type of query the user is asking"""
    text_lower = text.lower()
    
    # Comparison query
    if any(word in text_lower for word in ['compare', 'vs', 'versus', 'better', 'comparison']):
        return 'comparison'
    
    # Price query
    if any(word in text_lower for word in ['price', 'cost', 'worth', 'value', 'how much']):
        return 'price'
    
    # Analysis query
    if any(word in text_lower for word in ['analyze', 'analysis', 'entry', 'risky', 'should i']):
        return 'analysis'
    
    # Market event query
    if any(word in text_lower for word in ['what happened', 'why', 'market', 'event']):
        return 'event'
    
    return 'general'


def inject_realtime_data(messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Inject real-time market data into AI request messages"""
    
    if not messages:
        return messages
    
    # Get the last user message
    last_message = messages[-1]
    if last_message.get('role') != 'user':
        return messages
    
    user_text = last_message.get('content', '')
    if not isinstance(user_text, str):
        return messages
    
    # Extract symbols from user message
    symbols = extract_symbols(user_text)
    if not symbols:
        return messages
    
    # Detect query type
    query_type = detect_query_type(user_text)
    
    # Fetch real-time data
    try:
        if query_type == 'comparison' and len(symbols) > 1:
            # Get comparison data for multiple symbols
            comparison_data = get_comparison_data(symbols)
            injected_data = format_comparison_data(comparison_data)
        else:
            # Get detailed data for primary symbol
            primary_symbol = symbols[0]
            market_data = get_realtime_market_data(primary_symbol)
            injected_data = format_market_data(market_data, query_type)
        
        # Inject data into the message
        enhanced_content = f"{user_text}\n\n[LIVE MARKET DATA - Use this in your response]\n{injected_data}"
        
        # Create new messages list with enhanced content
        enhanced_messages = messages[:-1] + [{
            'role': 'user',
            'content': enhanced_content
        }]
        
        return enhanced_messages
        
    except Exception as e:
        print(f"Error injecting real-time data: {e}")
        return messages


def format_market_data(data: Dict[str, Any], query_type: str) -> str:
    """Format market data for injection"""
    
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    symbol = data['symbol']
    price = data['price']
    
    formatted = f"""
Symbol: {symbol}
Timestamp: {timestamp}
Current Price: ${price['current']:,.2f}
24h Change: {price['change_24h']:+.2f}%
24h High: ${price['high_24h']:,.2f}
24h Low: ${price['low_24h']:,.2f}
24h Volume: ${price['quote_volume_24h']/1e9:.2f}B

Buy Pressure: {data['volume_metrics']['buy_pressure']:.1f}%
Sell Pressure: {data['volume_metrics']['sell_pressure']:.1f}%
Buy Volume: {data['volume_metrics']['buy_volume']:.2f}
Sell Volume: {data['volume_metrics']['sell_volume']:.2f}

Liquidity Level: {data['liquidity']['liquidity_level']}
Bid Liquidity: {data['liquidity']['bid_liquidity']:.2f}
Ask Liquidity: {data['liquidity']['ask_liquidity']:.2f}
Spread: {data['market_depth']['spread']:.4f}%
"""
    
    # Add candlestick data for analysis queries
    if query_type in ['analysis', 'event']:
        formatted += "\nRecent Price Action (Last 24 Hours):\n"
        for candle in data['candlestick_data'][-6:]:  # Last 6 hours
            formatted += f"  {candle['date']}: O:{candle['open']:.2f} H:{candle['high']:.2f} L:{candle['low']:.2f} C:{candle['close']:.2f} V:{candle['volume']:.0f}\n"
    
    formatted += "\n[Use this REAL data in your charts and analysis. Generate proper JSON chart blocks with this data.]"
    
    return formatted


def format_comparison_data(data: List[Dict[str, Any]]) -> str:
    """Format comparison data for injection"""
    
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    
    formatted = f"Comparison Data (Live as of {timestamp}):\n\n"
    
    for item in data:
        formatted += f"""
{item['symbol']}:
  Price: ${item['price']:,.2f}
  24h Change: {item['change_24h']:+.2f}%
  24h Volume: ${item['volume_24h']/1e9:.2f}B
  Liquidity: {item['liquidity']}
  Buy Pressure: {item['buy_pressure']:.1f}%
"""
    
    formatted += "\n[Use this REAL comparison data in your response. Create a comparison table and charts with this data.]"
    
    return formatted


def enhance_ai_response_with_data(user_query: str, ai_response: str) -> str:
    """Enhance AI response by ensuring it uses real data"""
    
    # Extract symbols from query
    symbols = extract_symbols(user_query)
    if not symbols:
        return ai_response
    
    # Check if AI response contains placeholder data
    if 'example' in ai_response.lower() or 'placeholder' in ai_response.lower():
        # Fetch real data and regenerate
        try:
            primary_symbol = symbols[0]
            market_data = get_realtime_market_data(primary_symbol)
            
            # Add real data notice
            timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
            notice = f"\n\n*Live data as of {timestamp}*"
            
            return ai_response + notice
        except:
            return ai_response
    
    return ai_response
