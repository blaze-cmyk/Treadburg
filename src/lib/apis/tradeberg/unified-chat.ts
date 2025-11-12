/**
 * Unified TradeBerg Chat API Client
 * Handles both text queries (Perplexity) and image analysis (OpenAI Vision)
 * Clean, production-ready implementation
 */

import { WEBUI_API_BASE_URL } from '$lib/constants';

const TRADEBERG_API_BASE = `${WEBUI_API_BASE_URL}/api/tradeberg`;

export interface Message {
	role: 'system' | 'user' | 'assistant';
	content: string | MessageContent[];
}

export interface MessageContent {
	type: 'text' | 'image_url';
	text?: string;
	image_url?: {
		url: string;
		detail?: 'low' | 'high' | 'auto';
	};
}

export interface UnifiedChatRequest {
	messages: Message[];
	model?: string;
	temperature?: number;
	max_tokens?: number;
}

export interface UnifiedChatResponse {
	id: string;
	object: string;
	created: number;
	model: string;
	choices: {
		index: number;
		message: {
			role: string;
			content: string;
		};
		finish_reason: string;
	}[];
	usage: {
		prompt_tokens: number;
		completion_tokens: number;
		total_tokens: number;
	};
}

export interface Citation {
	title?: string;
	url: string;
	snippet?: string;
}

export interface ParsedResponse {
	content: string;
	citations: Citation[];
	relatedQuestions: string[];
	serviceUsed: 'openai_vision' | 'perplexity_api' | 'unknown';
}

/**
 * Send unified chat request to TradeBerg
 * Automatically routes between OpenAI Vision (images) and Perplexity (text/financial data)
 */
export async function sendUnifiedChat(
	request: UnifiedChatRequest,
	token: string = ''
): Promise<UnifiedChatResponse> {
	try {
		const response = await fetch(`${TRADEBERG_API_BASE}/enforced/chat/completions`, {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
				...(token && { Authorization: `Bearer ${token}` })
			},
			body: JSON.stringify(request)
		});

		if (!response.ok) {
			const error = await response.json();
			throw new Error(error.error || `HTTP ${response.status}: ${response.statusText}`);
		}

		return await response.json();
	} catch (error) {
		console.error('TradeBerg Unified Chat Error:', error);
		throw error;
	}
}

/**
 * Parse response to extract content, citations, and related questions
 */
export function parseUnifiedResponse(response: UnifiedChatResponse): ParsedResponse {
	const content = response.choices[0]?.message?.content || '';
	
	// Parse citations
	const citations: Citation[] = [];
	const citationsMatch = content.match(/\*\*📚 Sources:\*\*\n([\s\S]*?)(?=\n\n|$)/);
	if (citationsMatch) {
		const citationLines = citationsMatch[1].split('\n').filter(line => line.trim());
		citationLines.forEach(line => {
			const match = line.match(/\d+\.\s+(.+)/);
			if (match) {
				citations.push({ url: match[1].trim() });
			}
		});
	}
	
	// Parse related questions
	const relatedQuestions: string[] = [];
	const questionsMatch = content.match(/\*\*🔍 Related Questions:\*\*\n([\s\S]*?)(?=\n\n|$)/);
	if (questionsMatch) {
		const questionLines = questionsMatch[1].split('\n').filter(line => line.trim());
		questionLines.forEach(line => {
			const match = line.match(/•\s+(.+)/);
			if (match) {
				relatedQuestions.push(match[1].trim());
			}
		});
	}
	
	// Detect service used
	let serviceUsed: 'openai_vision' | 'perplexity_api' | 'unknown' = 'unknown';
	if (content.includes('(Openai Vision)')) {
		serviceUsed = 'openai_vision';
	} else if (content.includes('(Perplexity Api)')) {
		serviceUsed = 'perplexity_api';
	}
	
	// Clean content (remove metadata sections)
	let cleanContent = content
		.replace(/\*\*📚 Sources:\*\*\n[\s\S]*?(?=\n\n|$)/, '')
		.replace(/\*\*🔍 Related Questions:\*\*\n[\s\S]*?(?=\n\n|$)/, '')
		.trim();
	
	return {
		content: cleanContent,
		citations,
		relatedQuestions,
		serviceUsed
	};
}

/**
 * Create a text-only message
 */
export function createTextMessage(text: string, role: 'user' | 'assistant' = 'user'): Message {
	return {
		role,
		content: text
	};
}

/**
 * Create a message with both text and image
 */
export function createImageMessage(
	text: string,
	imageBase64: string,
	role: 'user' = 'user'
): Message {
	return {
		role,
		content: [
			{
				type: 'text',
				text
			},
			{
				type: 'image_url',
				image_url: {
					url: `data:image/png;base64,${imageBase64}`,
					detail: 'high'
				}
			}
		]
	};
}

/**
 * Convert a File to base64 string
 */
export async function fileToBase64(file: File): Promise<string> {
	return new Promise((resolve, reject) => {
		const reader = new FileReader();
		reader.readAsDataURL(file);
		reader.onload = () => {
			const result = reader.result as string;
			// Remove data:image/...;base64, prefix
			const base64 = result.split(',')[1];
			resolve(base64);
		};
		reader.onerror = (error) => reject(error);
	});
}

/**
 * Check TradeBerg API health
 */
export async function checkTradebergHealth(token: string = ''): Promise<any> {
	try {
		const response = await fetch(`${TRADEBERG_API_BASE}/test`, {
			method: 'GET',
			headers: {
				'Content-Type': 'application/json',
				...(token && { Authorization: `Bearer ${token}` })
			}
		});

		if (!response.ok) {
			throw new Error(`HTTP ${response.status}: ${response.statusText}`);
		}

		return await response.json();
	} catch (error) {
		console.error('TradeBerg Health Check Error:', error);
		throw error;
	}
}

/**
 * Format response for display with proper styling
 */
export function formatResponseForDisplay(parsed: ParsedResponse): string {
	let formatted = parsed.content;
	
	// Add citations section if available
	if (parsed.citations.length > 0) {
		formatted += '\n\n---\n\n**📚 Sources:**\n';
		parsed.citations.forEach((citation, index) => {
			formatted += `${index + 1}. [${citation.title || 'Source'}](${citation.url})\n`;
		});
	}
	
	// Add related questions if available
	if (parsed.relatedQuestions.length > 0) {
		formatted += '\n\n**🔍 You might also want to ask:**\n';
		parsed.relatedQuestions.forEach((question) => {
			formatted += `• ${question}\n`;
		});
	}
	
	return formatted;
}

// Export all utilities
export default {
	sendUnifiedChat,
	parseUnifiedResponse,
	createTextMessage,
	createImageMessage,
	fileToBase64,
	checkTradebergHealth,
	formatResponseForDisplay
};
