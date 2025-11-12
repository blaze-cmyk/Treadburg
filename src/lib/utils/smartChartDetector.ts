/**
 * Smart Chart Detector
 * Determines which chart system to use: AI-generated charts or TradingView fallback
 */

export interface SmartChartResult {
	showAICharts: boolean; // Show AI-generated D3/Plotly charts
	showTradingView: boolean; // Show TradingView widget
	symbol?: string;
	interval?: string;
	coinName?: string;
}

/**
 * Detect if AI response contains chart data
 */
export function hasAIGeneratedCharts(content: string): boolean {
	if (!content) return false;
	
	// Check for JSON chart blocks
	const chartPatterns = [
		/```json:chart:bar/i,
		/```json:chart:candlestick/i,
		/```json:chart:grid/i,
		/```json:chart:line/i
	];
	
	return chartPatterns.some(pattern => pattern.test(content));
}

/**
 * Detect if user is asking for a simple price check (show TradingView)
 */
function isSimplePriceCheck(message: string): boolean {
	if (!message) return false;
	
	const lowerMsg = message.toLowerCase().trim();
	
	// Simple price queries that should show TradingView
	const simplePricePatterns = [
		/^(what is|what's|whats) (the )?(current )?(btc|bitcoin|eth|ethereum|sol|solana) price/i,
		/^(btc|bitcoin|eth|ethereum|sol|solana) price$/i,
		/^price of (btc|bitcoin|eth|ethereum|sol|solana)$/i,
		/^show (me )?(btc|bitcoin|eth|ethereum|sol|solana) (price|chart)$/i
	];
	
	return simplePricePatterns.some(pattern => pattern.test(lowerMsg));
}

/**
 * Detect if user is asking for analysis (should use AI charts)
 */
function isAnalysisQuery(message: string): boolean {
	if (!message) return false;
	
	const lowerMsg = message.toLowerCase();
	
	const analysisKeywords = [
		'analyze',
		'analysis',
		'what happened',
		'why did',
		'explain',
		'entry',
		'exit',
		'risky',
		'safe',
		'should i',
		'recommend',
		'support',
		'resistance',
		'indicator',
		'pattern',
		'trend',
		'strategy'
	];
	
	return analysisKeywords.some(keyword => lowerMsg.includes(keyword));
}

const SYMBOL_MAP: Record<string, { symbol: string; name: string }> = {
	'btc': { symbol: 'BINANCE:BTCUSDT', name: 'Bitcoin' },
	'bitcoin': { symbol: 'BINANCE:BTCUSDT', name: 'Bitcoin' },
	'eth': { symbol: 'BINANCE:ETHUSDT', name: 'Ethereum' },
	'ethereum': { symbol: 'BINANCE:ETHUSDT', name: 'Ethereum' },
	'sol': { symbol: 'BINANCE:SOLUSDT', name: 'Solana' },
	'solana': { symbol: 'BINANCE:SOLUSDT', name: 'Solana' },
	'bnb': { symbol: 'BINANCE:BNBUSDT', name: 'BNB' },
	'xrp': { symbol: 'BINANCE:XRPUSDT', name: 'XRP' },
	'ada': { symbol: 'BINANCE:ADAUSDT', name: 'Cardano' },
	'cardano': { symbol: 'BINANCE:ADAUSDT', name: 'Cardano' }
};

/**
 * Extract symbol from message
 */
function extractSymbol(message: string): { symbol: string; name: string } {
	const lowerMsg = message.toLowerCase();
	
	for (const [key, value] of Object.entries(SYMBOL_MAP)) {
		if (lowerMsg.includes(key)) {
			return value;
		}
	}
	
	return { symbol: 'BINANCE:BTCUSDT', name: 'Bitcoin' };
}

/**
 * Main smart chart detection function
 * Call this to determine which chart system to use
 */
export function detectSmartChart(
	userMessage: string,
	aiResponse: string
): SmartChartResult {
	// Priority 1: If AI generated charts, use those
	if (hasAIGeneratedCharts(aiResponse)) {
		return {
			showAICharts: true,
			showTradingView: false
		};
	}
	
	// Priority 2: If user asked for analysis, wait for AI charts (don't show TradingView)
	if (isAnalysisQuery(userMessage)) {
		return {
			showAICharts: false,
			showTradingView: false // Don't show TradingView for analysis queries
		};
	}
	
	// Priority 3: If simple price check, show TradingView
	if (isSimplePriceCheck(userMessage)) {
		const { symbol, name } = extractSymbol(userMessage);
		return {
			showAICharts: false,
			showTradingView: true,
			symbol,
			coinName: name,
			interval: '15'
		};
	}
	
	// Default: Don't show any charts
	return {
		showAICharts: false,
		showTradingView: false
	};
}

/**
 * Helper to check if message should trigger any chart
 */
export function shouldShowAnyChart(userMessage: string, aiResponse: string): boolean {
	const result = detectSmartChart(userMessage, aiResponse);
	return result.showAICharts || result.showTradingView;
}
