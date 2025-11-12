/**
 * Detect if a message is asking about cryptocurrency prices
 * and extract the symbol for TradingView chart display
 */

export interface PriceQueryResult {
	isPriceQuery: boolean;
	symbol?: string;
	interval?: string;
	coinName?: string;
}

const PRICE_KEYWORDS = [
	'price', 'rate', 'cost', 'worth', 'value', 'trading',
	'chart', 'graph', 'btc', 'bitcoin', 'eth', 'ethereum',
	'market', 'current', 'now', 'today'
];

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
	'cardano': { symbol: 'BINANCE:ADAUSDT', name: 'Cardano' },
	'doge': { symbol: 'BINANCE:DOGEUSDT', name: 'Dogecoin' },
	'dogecoin': { symbol: 'BINANCE:DOGEUSDT', name: 'Dogecoin' },
	'dot': { symbol: 'BINANCE:DOTUSDT', name: 'Polkadot' },
	'polkadot': { symbol: 'BINANCE:DOTUSDT', name: 'Polkadot' },
	'matic': { symbol: 'BINANCE:MATICUSDT', name: 'Polygon' },
	'polygon': { symbol: 'BINANCE:MATICUSDT', name: 'Polygon' },
	'avax': { symbol: 'BINANCE:AVAXUSDT', name: 'Avalanche' },
	'avalanche': { symbol: 'BINANCE:AVAXUSDT', name: 'Avalanche' },
	'link': { symbol: 'BINANCE:LINKUSDT', name: 'Chainlink' },
	'chainlink': { symbol: 'BINANCE:LINKUSDT', name: 'Chainlink' },
	'uni': { symbol: 'BINANCE:UNIUSDT', name: 'Uniswap' },
	'uniswap': { symbol: 'BINANCE:UNIUSDT', name: 'Uniswap' }
};

/**
 * Detect if a message is asking about cryptocurrency prices
 */
export function detectPriceQuery(message: string): PriceQueryResult {
	if (!message || typeof message !== 'string') {
		return { isPriceQuery: false };
	}

	const lowerMsg = message.toLowerCase().trim();

	// Check if message contains price-related keywords
	const hasPriceKeyword = PRICE_KEYWORDS.some(keyword => lowerMsg.includes(keyword));

	if (!hasPriceKeyword) {
		return { isPriceQuery: false };
	}

	// Extract cryptocurrency symbol
	let detectedSymbol = 'BINANCE:BTCUSDT'; // Default to Bitcoin
	let detectedName = 'Bitcoin';

	for (const [key, value] of Object.entries(SYMBOL_MAP)) {
		if (lowerMsg.includes(key)) {
			detectedSymbol = value.symbol;
			detectedName = value.name;
			break;
		}
	}

	// Detect timeframe/interval
	let interval = '15'; // Default 15 minutes
	if (lowerMsg.includes('hour') || lowerMsg.includes('1h')) {
		interval = '60';
	} else if (lowerMsg.includes('day') || lowerMsg.includes('1d') || lowerMsg.includes('daily')) {
		interval = 'D';
	} else if (lowerMsg.includes('week') || lowerMsg.includes('1w') || lowerMsg.includes('weekly')) {
		interval = 'W';
	} else if (lowerMsg.includes('month') || lowerMsg.includes('1m') || lowerMsg.includes('monthly')) {
		interval = 'M';
	}

	return {
		isPriceQuery: true,
		symbol: detectedSymbol,
		interval,
		coinName: detectedName
	};
}

/**
 * Check if we should show chart for a given message pair
 */
export function shouldShowChart(userMessage: string, assistantMessage: string): PriceQueryResult {
	// Only show chart if user asked about price and assistant responded
	if (!userMessage || !assistantMessage) {
		return { isPriceQuery: false };
	}

	return detectPriceQuery(userMessage);
}
