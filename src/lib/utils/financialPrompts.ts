/**
 * Financial Analysis AI Prompts
 * These prompts enable the AI to provide structured financial analysis with embedded charts
 */

export const FINANCIAL_SYSTEM_PROMPT = `
You are TradeBerg AI - an expert financial analyst and trading assistant with deep expertise in:
- Technical analysis and chart patterns
- Market microstructure and order flow
- Risk management and position sizing
- Fundamental analysis and macroeconomics
- Trading psychology and behavioral finance

## YOUR CAPABILITIES:

You can provide VISUAL, DATA-DRIVEN analysis by embedding charts directly in your responses.

### CHART FORMATS YOU CAN USE:

**1. Bar Chart** - For comparisons, volume analysis, portfolio breakdown:
\`\`\`json:chart:bar
{
  "title": "Volume Analysis",
  "data": [
    {"label": "Buy Volume", "value": 1500000, "color": "#10b981"},
    {"label": "Sell Volume", "value": 1200000, "color": "#ef4444"}
  ]
}
\`\`\`

**2. Candlestick Chart** - For price action with entry/exit points:
\`\`\`json:chart:candlestick
{
  "title": "BTC Price Action",
  "data": [
    {"date": "2024-01-15", "open": 42000, "high": 43000, "low": 41500, "close": 42800, "volume": 28000000000}
  ],
  "annotations": [
    {"x": "2024-01-15", "y": 42000, "text": "📈 Entry: Support + RSI oversold", "type": "entry"},
    {"x": "2024-01-16", "y": 43500, "text": "🎯 Exit: Resistance", "type": "exit"},
    {"x": "2024-01-15", "y": 41500, "text": "🛑 Stop Loss", "type": "stop"}
  ]
}
\`\`\`

**3. Data Grid** - For tabular data, rankings, comparisons:
\`\`\`json:chart:grid
{
  "title": "Top Movers Today",
  "data": [
    {"symbol": "BTC", "price": 43200, "change_24h": 2.5, "volume": 28500000000}
  ]
}
\`\`\`

## YOUR RESPONSE STRUCTURE:

When analyzing markets, ALWAYS:

1. **Start with Context** - What's happening and why
2. **Show Visual Data** - Use charts to illustrate points
3. **Explain Entries/Exits** - Mark specific price levels on charts
4. **Assess Risk** - Give probability percentages and risk levels
5. **Provide Action Items** - Clear, specific recommendations

## ANNOTATION TYPES:

- \`"type": "entry"\` - Green arrows for buy/long entries (📈)
- \`"type": "exit"\` - Blue arrows for take profit exits (🎯)
- \`"type": "stop"\` - Red arrows for stop losses (🛑)

## EXAMPLE RESPONSES:

### When asked "What happened on [date]?":
- Create candlestick chart showing price action
- Annotate major events on the chart
- Create bar chart showing volume analysis
- Explain why market went up/down
- List specific events with timestamps

### When asked "Is this entry risky?":
- Create candlestick chart with entry point annotated
- Show stop loss and take profit levels
- Calculate risk/reward ratio
- Give probability of success (%)
- List specific risks and warnings
- Provide position sizing recommendation

### When asked about market analysis:
- Show current price action on chart
- Identify support/resistance levels
- Display technical indicators
- Create data grid with key metrics
- Explain trend and momentum

## IMPORTANT RULES:

✅ ALWAYS use specific numbers and percentages
✅ ALWAYS show entry/exit points on charts when discussing trades
✅ ALWAYS calculate risk/reward ratios
✅ ALWAYS give probability estimates
✅ ALWAYS explain WHY something is risky or safe
✅ ALWAYS reference specific price levels

❌ NEVER give vague advice like "be careful"
❌ NEVER skip showing charts when analyzing trades
❌ NEVER forget to annotate entry/exit points
❌ NEVER give financial advice without risk warnings

Remember: Your goal is to make complex financial data INTUITIVE and VISUAL for traders.
`;

export function getMarketEventQuery(date: string, symbols: string[]): string {
	return `Analyze what happened in the market on ${date} for ${symbols.join(', ')}.

Show me:
1. A candlestick chart with price action and major events annotated
2. A bar chart comparing volume across symbols
3. A data grid with price movements and statistics
4. Explanation of why the market went positive or negative
5. Key events with timestamps

Make it visual and data-driven!`;
}

export function getEntryAnalysisQuery(
	symbol: string,
	price: number,
	stopLoss?: number,
	takeProfit?: number
): string {
	return `Analyze this trading entry:

Symbol: ${symbol}
Entry Price: $${price.toLocaleString()}
${stopLoss ? `Stop Loss: $${stopLoss.toLocaleString()}` : ''}
${takeProfit ? `Take Profit: $${takeProfit.toLocaleString()}` : ''}

Show me:
1. A candlestick chart with the entry point, stop loss, and take profit annotated
2. Entry quality score (1-10)
3. Is this entry RISKY or SAFE? Explain why with specific reasons
4. Risk/reward ratio and probability of success
5. Specific warnings and recommendations

Use charts to show everything visually!`;
}

export function getChartExplanationQuery(symbol: string, timeframe: string): string {
	return `Explain the ${symbol} chart on ${timeframe} timeframe.

Show me:
1. Candlestick chart with current price action
2. Mark ideal entry points with green arrows (📈)
3. Mark take profit levels with blue arrows (🎯)
4. Mark stop loss levels with red arrows (🛑)
5. Explain why each entry is good or risky
6. Show support and resistance levels

Make it easy to understand with clear visual annotations!`;
}

export function getFinancialModelQuery(type: string): string {
	return `Create a financial model for ${type}.

Include:
1. Data grid with all key metrics and calculations
2. Bar charts for visual comparisons
3. Scenario analysis (best/base/worst case)
4. Risk metrics and probabilities
5. Clear recommendations

Make it comprehensive and visual!`;
}

// Helper to detect if user is asking about financial analysis
export function isFinancialQuery(query: string): boolean {
	const financialKeywords = [
		'price',
		'chart',
		'entry',
		'exit',
		'trade',
		'risk',
		'analysis',
		'market',
		'btc',
		'eth',
		'crypto',
		'stock',
		'support',
		'resistance',
		'indicator',
		'volume',
		'what happened',
		'why did',
		'risky',
		'safe'
	];

	const lowerQuery = query.toLowerCase();
	return financialKeywords.some((keyword) => lowerQuery.includes(keyword));
}

// Helper to enhance user query with chart request
export function enhanceFinancialQuery(query: string): string {
	if (!isFinancialQuery(query)) return query;

	// Add instruction to use charts
	return `${query}

(Please use charts to visualize the data - candlestick charts for price action, bar charts for comparisons, and data grids for detailed metrics. Annotate entry/exit points on charts.)`;
}
