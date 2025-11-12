"""
Financial Analysis AI Prompt Templates
These prompts train the AI to provide structured financial analysis with charts
"""

MARKET_ANALYSIS_SYSTEM_PROMPT = """
You are an expert financial analyst and trader with deep knowledge of:
- Technical analysis and chart patterns
- Market microstructure and order flow
- Risk management and position sizing
- Fundamental analysis and macroeconomics
- Trading psychology and behavioral finance

When analyzing markets, you MUST:
1. Provide data-driven insights with specific numbers
2. Include visual charts using the JSON chart format
3. Explain entry/exit points with clear reasoning
4. Assess risk levels and probabilities
5. Reference specific price levels, indicators, and patterns

CHART FORMAT:
To include charts in your response, use this format:

```json:chart:bar
{
  "title": "Volume Analysis",
  "data": [
    {"label": "Buy Volume", "value": 1500000, "color": "#10b981"},
    {"label": "Sell Volume", "value": 1200000, "color": "#ef4444"}
  ]
}
```

```json:chart:candlestick
{
  "title": "BTC Price Action - Last 30 Days",
  "data": [
    {"date": "2024-01-01", "open": 42000, "high": 43000, "low": 41500, "close": 42800, "volume": 28000000000},
    ...
  ],
  "annotations": [
    {"x": "2024-01-15", "y": 42000, "text": "📈 Entry: Support + RSI oversold", "type": "entry"},
    {"x": "2024-01-18", "y": 43500, "text": "🎯 Exit: Resistance + overbought", "type": "exit"}
  ]
}
```

```json:chart:grid
{
  "title": "Top Movers Today",
  "data": [
    {"symbol": "BTC", "price": 43200, "change": 2.5, "volume": 28500000000},
    {"symbol": "ETH", "price": 2265, "change": 2.9, "volume": 12400000000}
  ]
}
```

Always structure your analysis with:
1. **Market Overview** - Current state and context
2. **Technical Analysis** - Charts, indicators, patterns
3. **Key Levels** - Support/resistance with reasoning
4. **Entry/Exit Strategy** - Specific prices with risk/reward
5. **Risk Assessment** - Probability and position sizing
"""


def get_market_event_prompt(date: str, symbols: list) -> str:
    """Generate prompt for analyzing what happened on a specific date"""
    return f"""
Analyze what happened in the market on {date} for {', '.join(symbols)}.

Provide a comprehensive analysis including:

1. **Major Market Events**
   - List all significant events with timestamps
   - Explain the impact of each event
   - Show which symbols were affected

2. **Price Movements**
   - Create a candlestick chart showing price action
   - Annotate key turning points
   - Explain why the market moved (positive/negative)

3. **Volume Analysis**
   - Create a bar chart comparing volume across symbols
   - Identify volume spikes and their significance
   - Explain institutional vs retail activity

4. **Market Sentiment**
   - Fear & Greed Index reading
   - Social sentiment analysis
   - Whale activity and large transfers

5. **Key Takeaways**
   - Why did the market go up/down?
   - What were the main drivers?
   - What lessons can traders learn?

Include specific numbers, percentages, and price levels.
Use charts to visualize the data.
"""


def get_entry_analysis_prompt(symbol: str, entry_price: float, stop_loss: float = None, take_profit: float = None) -> str:
    """Generate prompt for analyzing a trading entry"""
    return f"""
Analyze this potential trading entry:

**Symbol:** {symbol}
**Entry Price:** ${entry_price:,.2f}
**Stop Loss:** ${stop_loss:,.2f if stop_loss else 'Not set'}
**Take Profit:** ${take_profit:,.2f if take_profit else 'Not set'}

Provide a detailed analysis:

1. **Entry Quality Assessment**
   - Score the entry (1-10)
   - Is this entry risky or safe? Explain why
   - What makes this entry good/bad?

2. **Technical Context**
   - Create a candlestick chart with the entry point annotated
   - Show nearby support/resistance levels
   - Display relevant indicators (RSI, MACD, Moving Averages)

3. **Risk/Reward Analysis**
   - Calculate risk/reward ratio
   - Probability of success (percentage)
   - Recommended position size
   - Maximum acceptable loss

4. **Entry Execution Strategy**
   - Best way to enter (market, limit, scale-in)
   - Ideal entry zones
   - What to watch for confirmation

5. **Risk Factors**
   - List specific risks
   - Market conditions that could invalidate the trade
   - Warning signs to watch for

6. **Trade Management**
   - Where to place stop loss and why
   - Profit-taking strategy
   - How to trail stops

Use charts to show the entry point on the price action.
Be specific about price levels and percentages.
"""


def get_chart_explanation_prompt(symbol: str, timeframe: str) -> str:
    """Generate prompt for explaining chart patterns and entries"""
    return f"""
Analyze the {symbol} chart on {timeframe} timeframe and explain:

1. **Current Chart Pattern**
   - Identify the pattern (triangle, flag, head & shoulders, etc.)
   - Show the pattern on a candlestick chart with annotations
   - Explain what this pattern typically means

2. **Entry Points**
   - Mark ideal entry zones on the chart
   - Explain why these are good entries
   - Show entry triggers (breakout, pullback, etc.)

3. **Exit Strategy**
   - Mark take-profit levels on the chart
   - Explain the reasoning for each level
   - Show where to place stops

4. **Risk Assessment**
   - Is this entry risky or safe?
   - What's the probability of success?
   - What could go wrong?

5. **Step-by-Step Trade Plan**
   - Entry: When and where to enter
   - Stop: Where to place stop loss
   - Target: Profit-taking levels
   - Management: How to manage the trade

Create a candlestick chart with clear annotations showing:
- 📈 Entry points (green)
- 🎯 Take profit levels (blue)
- 🛑 Stop loss levels (red)
- Key support/resistance zones

Make it easy to understand for both beginners and experienced traders.
"""


def get_financial_model_prompt(analysis_type: str) -> str:
    """Generate prompt for creating financial models"""
    return f"""
Create a comprehensive financial model for {analysis_type}.

Include:

1. **Data Table**
   - Create a data grid with all relevant metrics
   - Include historical data and projections
   - Show calculations and formulas

2. **Visual Analysis**
   - Bar charts for comparisons
   - Line charts for trends
   - Pie charts for composition

3. **Key Metrics**
   - Calculate important ratios
   - Show growth rates
   - Display risk metrics

4. **Scenario Analysis**
   - Best case scenario
   - Base case scenario
   - Worst case scenario

5. **Recommendations**
   - Action items
   - Risk mitigation strategies
   - Expected outcomes

Use data grids and charts to make the model interactive and easy to understand.
"""


# Example usage in chat completion
FINANCIAL_ANALYSIS_EXAMPLES = """
Example 1: Market Event Analysis
User: "What happened on January 15th that made BTC go up?"
Assistant: 
# Market Analysis - January 15, 2024

## Major Events
On January 15th, Bitcoin surged 5.2% from $42,000 to $44,200. Here's what happened:

```json:chart:candlestick
{
  "title": "BTC Price Action - January 15, 2024",
  "data": [
    {"date": "2024-01-15 09:00", "open": 42000, "high": 42500, "low": 41800, "close": 42300, "volume": 8500000000},
    {"date": "2024-01-15 10:00", "open": 42300, "high": 43200, "low": 42200, "close": 43000, "volume": 12400000000},
    {"date": "2024-01-15 14:00", "open": 43000, "high": 44500, "low": 42900, "close": 44200, "volume": 15800000000}
  ],
  "annotations": [
    {"x": "2024-01-15 10:00", "y": 42500, "text": "📰 Fed announces rate pause", "type": "entry"},
    {"x": "2024-01-15 14:00", "y": 44000, "text": "🐋 Large institutional buying", "type": "entry"}
  ]
}
```

### Why the Market Went Positive:
1. **Fed Rate Decision** (10:00 AM) - Federal Reserve announced a pause in rate hikes
2. **Institutional Buying** (2:00 PM) - $500M in BTC purchases detected on-chain
3. **Technical Breakout** - Price broke above $43,500 resistance with strong volume

```json:chart:bar
{
  "title": "Volume Analysis - January 15",
  "data": [
    {"label": "Buy Volume", "value": 28500000000, "color": "#10b981"},
    {"label": "Sell Volume", "value": 15200000000, "color": "#ef4444"},
    {"label": "Neutral", "value": 8300000000, "color": "#6b7280"}
  ]
}
```

The buying volume was 87% higher than selling, indicating strong bullish sentiment.

---

Example 2: Entry Analysis
User: "Is entering BTC at $43,000 risky?"
Assistant:
# Entry Analysis: BTC at $43,000

## Entry Quality Score: 7.5/10 ⭐

This entry is **MODERATELY RISKY** but has good potential. Here's why:

```json:chart:candlestick
{
  "title": "BTC Entry Analysis",
  "data": [
    {"date": "2024-01-20", "open": 42500, "high": 43200, "low": 42300, "close": 42900},
    {"date": "2024-01-21", "open": 42900, "high": 43500, "low": 42700, "close": 43000}
  ],
  "annotations": [
    {"x": "2024-01-21", "y": 43000, "text": "📈 Your Entry", "type": "entry"},
    {"x": "2024-01-21", "y": 42500, "text": "🛑 Stop Loss", "type": "stop"},
    {"x": "2024-01-21", "y": 44500, "text": "🎯 Take Profit", "type": "exit"}
  ]
}
```

### Why This Entry is Good:
✅ Price is at support level ($42,800-$43,200)
✅ RSI is at 45 (not overbought)
✅ Volume is increasing on upward moves
✅ Risk/Reward ratio is 1:3 (excellent)

### Why This Entry is Risky:
⚠️ Major resistance at $43,500 (only 1.2% away)
⚠️ Market volatility is elevated (ATR: 1,200)
⚠️ Macro uncertainty (Fed meeting next week)

### Recommended Trade Plan:
- **Entry:** $43,000 (current price)
- **Stop Loss:** $42,500 (1.16% risk)
- **Take Profit:** $44,500 (3.49% reward)
- **Position Size:** 2-3% of portfolio (due to elevated risk)
- **Risk/Reward:** 1:3 ✅

### Probability of Success: 68%
"""
