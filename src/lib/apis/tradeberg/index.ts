/**
 * TradeBerg Chart Analysis API
 * 
 * This module provides silent chart analysis capabilities:
 * - Automatically detects when user asks for chart analysis
 * - Captures TradingView screenshots in background (invisible to user)
 * - Sends to Vision API for analysis
 * - Returns only text analysis (screenshot never shown in UI)
 */

import { WEBUI_BASE_URL } from '$lib/constants';

const API_BASE_URL = WEBUI_BASE_URL;

export type VisionProvider = 'auto' | 'openai' | 'claude' | 'qwen' | 'deepseek' | 'perplexity';

export interface ChartAnalysisRequest {
	user_message: string;
	symbol?: string;
	timeframe?: string;
	use_vision?: boolean;
	vision_provider?: VisionProvider;
	use_cache?: boolean;
	frontend_url?: string;
}

export interface ChartAnalysisResponse {
	analysis: string;
	symbol: string;
	timeframe: string;
	method: 'vision_api' | 'web_scraping_fallback' | 'error';
	provider?: string;
	model?: string;
	tokens_used?: number;
	cost?: number;
	from_cache?: boolean;
	processing_time?: number;
	has_market_context?: boolean;
	citations?: string[];
	timestamp?: string;
	success: boolean;
	used_vision?: boolean;
	error?: string;
}

export interface CacheStats {
	cached_items: number;
	oldest_cache: number | null;
	newest_cache: number | null;
	rate_limits: Record<string, number>;
}

/**
 * Analyzes a chart silently in the background
 * 
 * This function:
 * 1. Sends request to backend
 * 2. Backend captures screenshot (user never sees it)
 * 3. Backend analyzes with Vision API
 * 4. Returns ONLY text analysis
 * 
 * @param request - Chart analysis request parameters
 * @param token - Authentication token (optional)
 * @returns Promise with analysis text
 */
export const analyzeChartSilently = async (
	request: ChartAnalysisRequest,
	token?: string
): Promise<ChartAnalysisResponse> => {
	try {
		console.log('📊 [TradeBerg] Silently analyzing chart:', request.symbol);

		const headers: HeadersInit = {
			'Content-Type': 'application/json'
		};

		if (token) {
			headers['Authorization'] = `Bearer ${token}`;
		}

		const response = await fetch(`${API_BASE_URL}/api/tradeberg/analyze-chart`, {
			method: 'POST',
			headers,
			body: JSON.stringify({
				symbol: request.symbol || 'BTCUSDT',
				timeframe: request.timeframe || '15m',
				user_prompt: request.user_message,
				vision_provider: request.vision_provider || 'auto', // Default to auto (Perplexity first)
				use_cache: request.use_cache !== false, // Default to true
				cache_ttl: 300
			})
		});

		if (!response.ok) {
			const errorData = await response.json().catch(() => ({}));
			throw new Error(errorData.detail || `Analysis failed: ${response.status}`);
		}

		const result: ChartAnalysisResponse = await response.json();

		console.log(
			`✅ [TradeBerg] Analysis complete (${result.method}/${result.provider}) - ${result.tokens_used || 0} tokens, $${result.cost?.toFixed(4) || '0.0000'}, ${result.has_market_context ? 'with market context' : 'technical only'}`
		);

		return result;
	} catch (error) {
		console.error('❌ [TradeBerg] Chart analysis error:', error);
		throw error;
	}
};

/**
 * Detects if user message requires chart analysis
 * 
 * @param message - User's message text
 * @returns True if chart analysis should be triggered
 */
export const shouldAnalyzeChart = (message: string): boolean => {
	if (!message) return false;

	const lowerMessage = message.toLowerCase();

	// Keywords that trigger chart analysis
	const analysisKeywords = [
		'analyze',
		'analysis',
		'trend',
		'trending',
		'support',
		'resistance',
		'breakout',
		'breakdown',
		'buy',
		'sell',
		'entry',
		'exit',
		'signal',
		'pattern',
		'chart',
		'technical',
		'indicator',
		'bullish',
		'bearish',
		'reversal',
		'liquidity',
		'sweep',
		'absorption',
		'imbalance',
		'level',
		'levels',
		'setup',
		'trade'
	];

	// Check for keywords
	const hasKeyword = analysisKeywords.some((keyword) => lowerMessage.includes(keyword));

	// Check for question patterns
	const questionPatterns = [
		'what do you see',
		"what's happening",
		'should i',
		'can i',
		'is it good',
		'looks like',
		'think about',
		'what about',
		'how is',
		'tell me about'
	];

	const hasQuestionPattern = questionPatterns.some((pattern) => lowerMessage.includes(pattern));

	// Check for symbol mentions (e.g., $BTC, BTCUSDT)
	const symbolPattern = /\$?[A-Z]{2,10}(?:USDT|USD|BTC|ETH)?/i;
	const hasSymbol = symbolPattern.test(message);

	// Check for timeframe mentions
	const timeframePattern = /\b(1m|5m|15m|30m|1h|4h|1d|1w|1M)\b/i;
	const hasTimeframe = timeframePattern.test(message);

	return hasKeyword || hasQuestionPattern || (hasSymbol && hasTimeframe);
};

/**
 * Extracts trading symbol from user message
 * 
 * @param message - User's message text
 * @param defaultSymbol - Default symbol if none found
 * @returns Extracted symbol (e.g., "BTCUSDT")
 */
export const extractSymbol = (message: string, defaultSymbol: string = 'BTCUSDT'): string => {
	if (!message) return defaultSymbol;

	// Pattern for $SYMBOL or SYMBOLUSDT format
	const patterns = [
		/\$([A-Z]{2,10})(?:USDT|USD|BTC|ETH)?/i,
		/\b([A-Z]{2,10})(?:USDT|USD|BTC|ETH)\b/i,
		/\b([A-Z]{2,10})\b(?=\s*(?:chart|analysis|trend|setup))/i
	];

	for (const pattern of patterns) {
		const match = message.match(pattern);
		if (match) {
			let symbol = match[1].toUpperCase();
			// Normalize to USDT if not specified
			if (!['USDT', 'USD', 'BTC', 'ETH'].some((suffix) => symbol.endsWith(suffix))) {
				symbol = `${symbol}USDT`;
			}
			return symbol;
		}
	}

	return defaultSymbol;
};

/**
 * Extracts timeframe from user message
 * 
 * @param message - User's message text
 * @param defaultTimeframe - Default timeframe if none found
 * @returns Extracted timeframe (e.g., "15m", "1h", "1d")
 */
export const extractTimeframe = (message: string, defaultTimeframe: string = '15m'): string => {
	if (!message) return defaultTimeframe;

	const lowerMessage = message.toLowerCase();

	// Direct patterns
	const directPattern = /\b(1m|5m|15m|30m|1h|4h|1d|1w|1M)\b/i;
	const match = lowerMessage.match(directPattern);
	if (match) {
		return match[1];
	}

	// Minutes patterns
	const minutesMatch = lowerMessage.match(/\b(\d{1,2})\s*(?:m|min|mins|minute|minutes)\b/);
	if (minutesMatch) {
		return `${minutesMatch[1]}m`;
	}

	// Hours patterns
	const hoursMatch = lowerMessage.match(/\b(\d{1,2})\s*(?:h|hr|hrs|hour|hours)\b/);
	if (hoursMatch) {
		return `${hoursMatch[1]}h`;
	}

	// Days patterns
	const daysMatch = lowerMessage.match(/\b(\d{1,2})\s*(?:d|day|days)\b/);
	if (daysMatch) {
		return `${daysMatch[1]}d`;
	}

	return defaultTimeframe;
};

/**
 * Get vision cache statistics
 * 
 * @param token - Authentication token (optional)
 * @returns Promise with cache stats
 */
export const getCacheStats = async (token?: string): Promise<CacheStats> => {
	try {
		const headers: HeadersInit = {};
		if (token) {
			headers['Authorization'] = `Bearer ${token}`;
		}

		const response = await fetch(`${API_BASE_URL}/api/tradeberg/vision/cache/stats`, {
			method: 'GET',
			headers
		});

		if (!response.ok) {
			throw new Error(`Failed to get cache stats: ${response.status}`);
		}

		return await response.json();
	} catch (error) {
		console.error('❌ [TradeBerg] Failed to get cache stats:', error);
		throw error;
	}
};

/**
 * Clear vision analysis cache
 * 
 * @param token - Authentication token (optional)
 * @returns Promise with success message
 */
export const clearCache = async (token?: string): Promise<{ message: string }> => {
	try {
		const headers: HeadersInit = {};
		if (token) {
			headers['Authorization'] = `Bearer ${token}`;
		}

		const response = await fetch(`${API_BASE_URL}/api/tradeberg/vision/cache/clear`, {
			method: 'POST',
			headers
		});

		if (!response.ok) {
			throw new Error(`Failed to clear cache: ${response.status}`);
		}

		return await response.json();
	} catch (error) {
		console.error('❌ [TradeBerg] Failed to clear cache:', error);
		throw error;
	}
};

/**
 * Get available Vision API providers and their status
 * 
 * @param token - Authentication token (optional)
 * @returns Promise with provider information
 */
export const getVisionProviders = async (token?: string): Promise<{
	success: boolean;
	providers: Record<string, {
		name: string;
		cost_per_1k_tokens: number;
		rate_limit_per_minute: number;
		features: string[];
		configured: boolean;
	}>;
	default_fallback_chain: string[];
	recommended_for_trading: string;
}> => {
	try {
		const headers: HeadersInit = {};
		if (token) {
			headers['Authorization'] = `Bearer ${token}`;
		}

		const response = await fetch(`${API_BASE_URL}/api/tradeberg/vision/providers`, {
			method: 'GET',
			headers
		});

		if (!response.ok) {
			throw new Error(`Failed to get vision providers: ${response.status}`);
		}

		return await response.json();
	} catch (error) {
		console.error('❌ [TradeBerg] Failed to get vision providers:', error);
		throw error;
	}
};
