"""
Price data formatter with ASCII charts
"""
from typing import Dict, List
import math

class PriceFormatter:
    """Format price data with beautiful charts and tables"""
    
    @staticmethod
    def format_price_data(price_data: Dict) -> str:
        """Format single price data beautifully"""
        if not price_data:
            return "❌ Unable to fetch price data"
        
        symbol = price_data["symbol"].replace("USDT", "")
        price = price_data["price"]
        change = price_data["change_24h"]
        change_percent = price_data["change_percent_24h"]
        high = price_data["high_24h"]
        low = price_data["low_24h"]
        volume = price_data["volume_24h"]
        
        # Determine trend
        trend_emoji = "🟢" if change >= 0 else "🔴"
        trend_text = "UP" if change >= 0 else "DOWN"
        
        output = f"""# 💰 {symbol} Real-Time Price

## Current Price
**${price:,.2f}** {trend_emoji}

## 24H Performance

| Metric | Value |
|--------|-------|
| **Change** | {trend_emoji} ${change:,.2f} ({change_percent:+.2f}%) |
| **High** | ${high:,.2f} |
| **Low** | ${low:,.2f} |
| **Volume** | {volume:,.0f} {symbol} |

## Price Range (24H)

```
Low                                                    High
${low:,.2f} {PriceFormatter._create_range_bar(price, low, high)} ${high:,.2f}
```

## Trend: {trend_text} {trend_emoji}

---
*Data from Binance • Updated: {price_data["timestamp"]}*
"""
        return output
    
    @staticmethod
    def format_multiple_prices(prices_data: Dict[str, Dict]) -> str:
        """Format multiple prices in a comparison table"""
        if not prices_data:
            return "❌ Unable to fetch price data"
        
        output = "# 📊 Multi-Asset Price Overview\n\n"
        output += "| Symbol | Price | 24h Change | High | Low |\n"
        output += "|--------|-------|------------|------|-----|\n"
        
        for symbol, data in prices_data.items():
            clean_symbol = symbol.replace("USDT", "")
            price = data["price"]
            change_percent = data["change_percent_24h"]
            high = data["high_24h"]
            low = data["low_24h"]
            
            trend_emoji = "🟢" if change_percent >= 0 else "🔴"
            
            output += f"| **{clean_symbol}** | ${price:,.2f} | {trend_emoji} {change_percent:+.2f}% | ${high:,.2f} | ${low:,.2f} |\n"
        
        output += "\n---\n*Real-time data from Binance*\n"
        return output
    
    @staticmethod
    def format_price_chart(klines: List[Dict], symbol: str) -> str:
        """Create ASCII chart from candlestick data"""
        if not klines or len(klines) < 2:
            return "❌ Insufficient data for chart"
        
        clean_symbol = symbol.replace("USDT", "")
        
        # Extract closing prices
        prices = [k["close"] for k in klines]
        timestamps = [k["timestamp"].split("T")[1][:5] for k in klines[-10:]]  # Last 10 hours
        
        # Create ASCII chart
        output = f"""# 📈 {clean_symbol} Price Chart (Last {len(klines)} periods)

## Price Movement

```
{PriceFormatter._create_ascii_chart(prices[-10:], timestamps)}
```

## Statistics

| Metric | Value |
|--------|-------|
| **Current** | ${prices[-1]:,.2f} |
| **Highest** | ${max(prices):,.2f} |
| **Lowest** | ${min(prices):,.2f} |
| **Average** | ${sum(prices)/len(prices):,.2f} |
| **Change** | {((prices[-1] - prices[0]) / prices[0] * 100):+.2f}% |

"""
        return output
    
    @staticmethod
    def _create_range_bar(current: float, low: float, high: float, width: int = 40) -> str:
        """Create a visual range bar"""
        if high == low:
            return "█" * width
        
        # Calculate position
        position = int(((current - low) / (high - low)) * width)
        position = max(0, min(width - 1, position))
        
        bar = ""
        for i in range(width):
            if i == position:
                bar += "█"
            elif i < position:
                bar += "░"
            else:
                bar += "░"
        
        return bar
    
    @staticmethod
    def _create_ascii_chart(prices: List[float], labels: List[str], height: int = 10) -> str:
        """Create ASCII line chart"""
        if not prices or len(prices) < 2:
            return "Insufficient data"
        
        # Normalize prices to chart height
        min_price = min(prices)
        max_price = max(prices)
        price_range = max_price - min_price
        
        if price_range == 0:
            price_range = 1
        
        # Create chart lines
        chart_lines = []
        for row in range(height, -1, -1):
            line = ""
            threshold = min_price + (price_range * row / height)
            
            # Add price label
            if row == height:
                line = f"${max_price:>8,.0f} │"
            elif row == 0:
                line = f"${min_price:>8,.0f} │"
            else:
                line = "         │"
            
            # Plot points
            for i, price in enumerate(prices):
                normalized = (price - min_price) / price_range * height
                
                if abs(normalized - row) < 0.5:
                    line += "●"
                elif i > 0:
                    prev_normalized = (prices[i-1] - min_price) / price_range * height
                    if min(normalized, prev_normalized) <= row <= max(normalized, prev_normalized):
                        line += "│"
                    else:
                        line += " "
                else:
                    line += " "
            
            chart_lines.append(line)
        
        # Add time labels
        chart_lines.append("         └" + "─" * len(prices))
        
        # Add time labels (if provided)
        if labels and len(labels) == len(prices):
            time_line = "          "
            for i, label in enumerate(labels):
                if i % 2 == 0:  # Show every other label
                    time_line += label[:5]
                else:
                    time_line += "     "
            chart_lines.append(time_line)
        
        return "\n".join(chart_lines)
    
    @staticmethod
    def format_order_book(order_book: Dict) -> str:
        """Format order book data"""
        if not order_book:
            return "❌ Unable to fetch order book"
        
        symbol = order_book["symbol"].replace("USDT", "")
        bids = order_book["bids"][:5]
        asks = order_book["asks"][:5]
        
        output = f"""# 📖 {symbol} Order Book

## Asks (Sell Orders) 🔴

| Price | Amount |
|-------|--------|
"""
        for price, qty in reversed(asks):
            output += f"| ${price:,.2f} | {qty:.4f} |\n"
        
        output += "\n## Bids (Buy Orders) 🟢\n\n"
        output += "| Price | Amount |\n"
        output += "|-------|--------|\n"
        
        for price, qty in bids:
            output += f"| ${price:,.2f} | {qty:.4f} |\n"
        
        output += "\n---\n*Real-time order book from Binance*\n"
        return output
