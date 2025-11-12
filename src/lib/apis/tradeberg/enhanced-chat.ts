/**
 * Enhanced TradeBerg Chat API with Function Calling
 * Integrates OpenAI ChatGPT with Coinalyze and Nansen APIs for real-time market analysis
 */

import { WEBUI_BASE_URL } from '$lib/constants';

const API_BASE_URL = WEBUI_BASE_URL;

export interface ChatMessage {
	role: 'user' | 'assistant' | 'system' | 'function';
	content: string | null;
	function_call?: {
		name: string;
		arguments: string;
	};
	name?: string; // For function messages
}

export interface EnhancedChatRequest {
	messages: ChatMessage[];
	model?: string;
	temperature?: number;
	enable_functions?: boolean;
	session_id?: string;
	image_data?: string;
}

export interface Citation {
	title: string;
	url: string;
	snippet?: string;
}

export interface QueryInfo {
	query_types: string[];
	symbols: string[];
	timeframe: string;
	original_query: string;
}

export interface FunctionDefinition {
	name: string;
	description: string;
	parameters: {
		type: string;
		properties: Record<string, any>;
		required: string[];
	};
}

export interface EnhancedChatResponse {
	success: boolean;
	response: string;
	query_info?: QueryInfo;
	citations?: Citation[];
	related_questions?: string[];
	images?: Array<{url: string; title: string}>;
	function_called?: string;
	function_result?: any;
	usage?: {
		prompt_tokens?: number;
		completion_tokens?: number;
		total_tokens: number;
	};
	model?: string;
	error?: string;
}

export interface AvailableFunctionsResponse {
	success: boolean;
	functions: FunctionDefinition[];
	total_functions: number;
}

/**
 * Send enhanced chat request with function calling capabilities
 */
export const sendEnhancedChat = async (
	request: EnhancedChatRequest,
	token?: string
): Promise<EnhancedChatResponse> => {
	try {

		const headers: HeadersInit = {
			'Content-Type': 'application/json'
		};

		if (token) {
			headers['Authorization'] = `Bearer ${token}`;
		}

		const response = await fetch(`${API_BASE_URL}/api/tradeberg/enhanced-chat`, {
			method: 'POST',
			headers,
			body: JSON.stringify({
				messages: request.messages,
				model: request.model || 'gpt-4o',
				temperature: request.temperature || 0.1,
				enable_functions: request.enable_functions !== false
			})
		});

		if (!response.ok) {
			const errorData = await response.json().catch(() => ({}));
			throw new Error(errorData.detail || `Request failed: ${response.status}`);
		}

		const result: EnhancedChatResponse = await response.json();
		return result;
	} catch (error) {
		console.error('❌ [TradeBerg] Enhanced chat error:', error);
		throw error;
	}
};

/**
 * Get available market data functions
 */
export const getAvailableFunctions = async (token?: string): Promise<AvailableFunctionsResponse> => {
	try {

		const headers: HeadersInit = {};
		if (token) {
			headers['Authorization'] = `Bearer ${token}`;
		}

		const response = await fetch(`${API_BASE_URL}/api/tradeberg/available-functions`, {
			headers
		});

		if (!response.ok) {
			const errorData = await response.json().catch(() => ({}));
			throw new Error(errorData.detail || `Request failed: ${response.status}`);
		}

		const result: AvailableFunctionsResponse = await response.json();
		return result;
	} catch (error) {
		console.error('❌ [TradeBerg] Error fetching functions:', error);
		throw error;
	}
};

/**
 * Helper function to create market analysis messages
 */
export const createMarketAnalysisMessages = (
	userQuery: string,
	includeSystemPrompt: boolean = true
): ChatMessage[] => {
	const messages: ChatMessage[] = [];

	if (includeSystemPrompt) {
		messages.push({
			role: 'system',
			content: `You are TRADEBERG — an institutional AI terminal specialized in crypto market analysis. 

You have access to real-time market data through these functions:
- get_coinalyze_open_interest: Get open interest data for crypto symbols
- get_coinalyze_funding_rates: Get funding rates for perpetual futures
- get_coinalyze_liquidations: Get recent liquidation data
- get_nansen_defi_holdings: Get DeFi portfolio holdings for wallet addresses
- analyze_market_structure: Comprehensive market structure analysis

Always use institutional language and focus on:
- Liquidity analysis and market microstructure
- Institutional positioning and smart money flows
- Risk assessment and scenario planning
- Entry/exit levels with risk-reward ratios

When users ask about market data, automatically call the appropriate functions to get real-time information.`
		});
	}

	messages.push({
		role: 'user',
		content: userQuery
	});

	return messages;
};

/**
 * Predefined market analysis queries
 */
export const MARKET_ANALYSIS_QUERIES = {
	btc_structure: "Analyze the current market structure for BTCUSDT including open interest, funding rates, and recent liquidations",
	eth_structure: "Analyze the current market structure for ETHUSDT including open interest, funding rates, and recent liquidations",
	funding_analysis: "Get current funding rates for BTCUSDT and ETHUSDT and analyze the sentiment implications",
	liquidation_analysis: "Show me recent liquidations for BTCUSDT and explain what this means for price action",
	defi_whale_analysis: "Analyze DeFi holdings for this whale wallet: 0x...", // User needs to provide wallet
	multi_asset_analysis: "Compare market structure across BTCUSDT, ETHUSDT, and SOLUSDT"
};

/**
 * Helper to detect if a user query needs market data
 */
export const needsMarketData = (query: string): boolean => {
	const marketKeywords = [
		'open interest', 'funding rate', 'liquidation', 'market structure',
		'btc', 'eth', 'bitcoin', 'ethereum', 'usdt', 'defi', 'wallet',
		'position', 'leverage', 'futures', 'perpetual', 'analysis'
	];

	const lowerQuery = query.toLowerCase();
	return marketKeywords.some(keyword => lowerQuery.includes(keyword));
};

/**
 * Enhanced Perplexity Strategy Chat - Main function for new system
 */
export const sendPerplexityChat = async (
	userMessage: string,
	sessionId?: string,
	imageData?: string,
	token?: string
): Promise<EnhancedChatResponse> => {
	try {
		const headers: HeadersInit = {
			'Content-Type': 'application/json'
		};

		if (token) {
			headers['Authorization'] = `Bearer ${token}`;
		}

		const response = await fetch(`${API_BASE_URL}/api/tradeberg/chat/completions`, {
			method: 'POST',
			headers,
			body: JSON.stringify({
				messages: [
					{
						role: 'user',
						content: imageData ? [
							{ type: 'text', text: userMessage },
							{ type: 'image_url', image_url: { url: `data:image/png;base64,${imageData}` } }
						] : userMessage
					}
				],
				model: 'sonar-pro',
				session_id: sessionId || `session_${Date.now()}`,
				stream: false
			})
		});

		if (!response.ok) {
			const errorData = await response.json().catch(() => ({}));
			throw new Error(errorData.detail || `Request failed: ${response.status}`);
		}

		const result = await response.json();
		
		// Extract content from OpenAI-compatible response
		const content = result.choices?.[0]?.message?.content || '';
		
		return {
			success: true,
			response: content,
			usage: result.usage || { total_tokens: 0 },
			model: result.model || 'sonar-pro'
		};

	} catch (error) {
		console.error('❌ [TradeBerg] Perplexity chat error:', error);
		return {
			success: false,
			error: error instanceof Error ? error.message : 'Unknown error',
			response: 'I apologize, but I encountered an error processing your request. Please try again.'
		};
	}
};

/**
 * Enhanced chat with automatic function detection (Legacy support)
 */
export const sendSmartChat = async (
	userQuery: string,
	conversationHistory: ChatMessage[] = [],
	token?: string
): Promise<EnhancedChatResponse> => {
	try {
		// Use new Perplexity strategy by default
		return await sendPerplexityChat(userQuery, undefined, undefined, token);

	} catch (error) {
		console.error('❌ [TradeBerg] Smart chat error:', error);
		throw error;
	}
};

/**
 * Stream enhanced chat response (for future implementation)
 */
export const streamEnhancedChat = async function* (
	request: EnhancedChatRequest,
	token?: string
): AsyncGenerator<string, void, unknown> {
	// TODO: Implement streaming response
	// For now, fall back to regular response
	const response = await sendEnhancedChat(request, token);
	yield response.response;
};

/**
 * Parse related questions from response for UI display
 */
export const parseRelatedQuestions = (response: string): string[] => {
	const questions: string[] = [];
	const lines = response.split('\n');
	
	let inQuestionsSection = false;
	for (const line of lines) {
		if (line.includes('Related Questions') || line.includes('💡')) {
			inQuestionsSection = true;
			continue;
		}
		
		if (inQuestionsSection) {
			if (line.startsWith('- 🔍 **') || line.startsWith('- **')) {
				const question = line.replace(/^- 🔍 \*\*|\*\*$/g, '').trim();
				if (question) questions.push(question);
			} else if (line.startsWith('##') || line.startsWith('---')) {
				break;
			}
		}
	}
	
	return questions;
};

/**
 * Parse citations from response
 */
export const parseCitations = (response: string): Citation[] => {
	const citations: Citation[] = [];
	const lines = response.split('\n');
	
	let inCitationsSection = false;
	for (const line of lines) {
		if (line.includes('Sources & Citations') || line.includes('📚')) {
			inCitationsSection = true;
			continue;
		}
		
		if (inCitationsSection) {
			const match = line.match(/\d+\.\s*\*\*\[(.*?)\]\((.*?)\)\*\*/);
			if (match) {
				citations.push({
					title: match[1],
					url: match[2]
				});
			} else if (line.startsWith('##') || line.startsWith('---')) {
				break;
			}
		}
	}
	
	return citations;
};

/**
 * Image upload helper for chart analysis
 */
export const uploadImageForAnalysis = async (
	file: File,
	userMessage: string,
	sessionId?: string,
	token?: string
): Promise<EnhancedChatResponse> => {
	try {
		// Convert file to base64
		const base64 = await new Promise<string>((resolve, reject) => {
			const reader = new FileReader();
			reader.onload = () => {
				const result = reader.result as string;
				const base64Data = result.split(',')[1]; // Remove data:image/...;base64, prefix
				resolve(base64Data);
			};
			reader.onerror = reject;
			reader.readAsDataURL(file);
		});

		return await sendPerplexityChat(userMessage, sessionId, base64, token);

	} catch (error) {
		console.error('❌ [TradeBerg] Image upload error:', error);
		return {
			success: false,
			error: error instanceof Error ? error.message : 'Image upload failed',
			response: 'Failed to process the uploaded image. Please try again.'
		};
	}
};

/**
 * Quick analysis templates for common queries
 */
export const ENHANCED_ANALYSIS_TEMPLATES = {
	btc_analysis: "Analyze Bitcoin (BTC) current market conditions, price action, and key levels for trading opportunities",
	eth_analysis: "Analyze Ethereum (ETH) market structure, DeFi impact, and institutional positioning",
	market_overview: "Provide comprehensive crypto market overview with top performers, market sentiment, and key catalysts",
	chart_analysis: "Analyze this chart for technical patterns, key levels, entry/exit points, and risk assessment",
	news_impact: "Analyze recent crypto market news and their impact on major cryptocurrencies",
	defi_analysis: "Analyze current DeFi market conditions, yield opportunities, and protocol performance"
};

export default {
	sendEnhancedChat,
	sendPerplexityChat,
	getAvailableFunctions,
	createMarketAnalysisMessages,
	sendSmartChat,
	needsMarketData,
	parseRelatedQuestions,
	parseCitations,
	uploadImageForAnalysis,
	MARKET_ANALYSIS_QUERIES,
	ENHANCED_ANALYSIS_TEMPLATES
};
