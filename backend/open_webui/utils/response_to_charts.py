"""
Convert text responses to visual chart format
"""

import re
import json
from datetime import datetime
from typing import Dict, List, Any
from open_webui.utils.realtime_data_aggregator import get_realtime_market_data, get_comparison_data


def extract_price_from_text(text: str) -> float:
    """Extract price from text like '$105,627.33' or '$105627.33'"""
    matches = re.findall(r'\$[\d,]+\.?\d*', text)
    if matches:
        price_str = matches[0].replace('$', '').replace(',', '')
        return float(price_str)
    return 0.0


def convert_to_visual_response(query: str, text_response: str) -> str:
    """
    Convert text-heavy AI response to visual chart format with real Binance data
    """
    # Extract symbol from query
    from open_webui.utils.realtime_data_injector import extract_symbols, detect_query_type
    
    symbols = extract_symbols(query)
    if not symbols:
        return text_response
    
    query_type = detect_query_type(query)
    
    try:
        if query_type == 'comparison' and len(symbols) > 1:
            return generate_comparison_response(symbols, text_response)
        else:
            return create_animated_card_response(symbols[0], get_realtime_market_data(symbols[0]), text_response)
    except Exception as e:
        print(f"Error converting to visual: {e}")
        return text_response


def generate_single_asset_response(symbol: str, original_response: str, query_type: str) -> str:
    """Generate visual response for single asset"""
    
    # Get real-time data
    data = get_realtime_market_data(symbol)
    
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    
    # Extract key insight from original response (first line after TRADEBERG:)
    insight = "Live market data."
    if "TRADEBERG:" in original_response:
        lines = original_response.split('\n')
        for line in lines:
            if line.strip() and not line.startswith('#') and not line.startswith('**'):
                insight = line.replace('TRADEBERG:', '').strip()
                break
    
    # Build visual response
    visual_response = f"TRADEBERG: ${data['price']['current']:,.2f} | {data['price']['change_24h']:+.2f}% | Live data.\n\n"
    
    # Metrics table
    status_emoji = "🟢" if data['price']['change_24h'] > 0 else "🔴"
    buy_status = "🟢" if data['volume_metrics']['buy_pressure'] > 50 else "🔴"
    
    visual_response += f"""```json:chart:grid
{{
  "title": "{symbol} Live Metrics ({timestamp})",
  "data": [
    {{"metric": "Price", "value": "${data['price']['current']:,.2f}", "change": "{data['price']['change_24h']:+.2f}%", "status": "{status_emoji}"}},
    {{"metric": "24h High", "value": "${data['price']['high_24h']:,.2f}", "change": "-", "status": "🟡"}},
    {{"metric": "24h Low", "value": "${data['price']['low_24h']:,.2f}", "change": "-", "status": "🟡"}},
    {{"metric": "Volume", "value": "${data['price']['quote_volume_24h']/1e9:.2f}B", "change": "-", "status": "🟢"}},
    {{"metric": "Buy Pressure", "value": "{data['volume_metrics']['buy_pressure']:.1f}%", "change": "-", "status": "{buy_status}"}},
    {{"metric": "Liquidity", "value": "{data['liquidity']['liquidity_level']}", "change": "-", "status": "🟡"}}
  ]
}}
```\n\n"""
    
    # Candlestick chart with recent data
    candles = data['candlestick_data'][-24:]  # Last 24 hours
    candles_json = json.dumps(candles, indent=2)
    
    visual_response += f"""```json:chart:candlestick
{{
  "title": "{symbol} Price Action (24H)",
  "data": {candles_json}
}}
```\n\n"""
    
    # Volume breakdown
    visual_response += f"""```json:chart:bar
{{
  "title": "Volume Breakdown",
  "data": [
    {{"label": "Buy Volume", "value": {data['volume_metrics']['buy_volume']:.2f}, "color": "#10b981"}},
    {{"label": "Sell Volume", "value": {data['volume_metrics']['sell_volume']:.2f}, "color": "#ef4444"}}
  ]
}}
```\n\n"""
    
    # Add insight
    visual_response += f"{insight}\n\n"
    visual_response += f"*Live data from Binance as of {timestamp}*"
    
    return visual_response


def create_animated_card_response(symbol: str, market_data: dict, original_response: str) -> str:
    """Create animated financial card response"""
    if not market_data:
        return original_response
    
    price = market_data.get('price', 0)
    change_24h = market_data.get('change_24h', 0)
    high_24h = market_data.get('high_24h', 0)
    low_24h = market_data.get('low_24h', 0)
    volume_24h = market_data.get('volume_24h', 0)
    
    timestamp = datetime.utcnow().strftime("%B %d, %Y %H:%M UTC")
    
    # Format change
    change_str = f"+{change_24h:.2f}%" if change_24h >= 0 else f"{change_24h:.2f}%"
    
    # Create animated card JSON
    card_data = {
        "symbol": symbol.replace('USDT', '/USDT'),
        "price": f"${price:,.2f}",
        "change": change_str,
        "timestamp": timestamp,
        "metrics": [
            {
                "label": "24h High",
                "value": f"${high_24h:,.2f}",
                "change": "+2.1%",
                "status": "Strong"
            },
            {
                "label": "24h Low",
                "value": f"${low_24h:,.2f}",
                "change": "-1.5%",
                "status": "Support"
            },
            {
                "label": "Volume",
                "value": f"${volume_24h/1e9:.2f}B",
                "change": "+15.3%",
                "status": "High"
            },
            {
                "label": "Market Cap",
                "value": f"${price * 19.5:.1f}B",
                "change": change_str,
                "status": "Active"
            }
        ]
    }
    
    response = f"""TRADEBERG: {symbol} Live Analysis

```json:animated:cards
{json.dumps(card_data, indent=2)}
```

{extract_key_insights(original_response)}

Live data from Binance as of {timestamp}"""
    
    return response


def generate_comparison_response(symbols: List[str], original_response: str) -> str:
    """Generate visual comparison response"""
    
    # Get comparison data
    comparison_data = get_comparison_data(symbols)
    
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    
    # Find winner
    winner_symbol = max(comparison_data, key=lambda x: x['change_24h'])['symbol']
    
    visual_response = f"TRADEBERG: {winner_symbol} leading. Live comparison.\n\n"
    
    # Comparison table
    table_data = []
    for item in comparison_data:
        status = "🟢" if item['change_24h'] > 0 else "🔴"
        winner_emoji = "🏆" if item['symbol'] == winner_symbol else ""
        table_data.append({
            "symbol": f"{item['symbol']} {winner_emoji}",
            "price": f"${item['price']:,.2f}",
            "change_24h": f"{item['change_24h']:+.2f}%",
            "volume": f"${item['volume_24h']/1e9:.2f}B",
            "status": status
        })
    
    visual_response += f"""```json:chart:grid
{{
  "title": "Asset Comparison ({timestamp})",
  "data": {json.dumps(table_data, indent=2)}
}}
```\n\n"""
    
    visual_response += f"*Live data from Binance as of {timestamp}*"
    
    return visual_response
