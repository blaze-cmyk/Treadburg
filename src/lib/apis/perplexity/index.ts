/**
 * Perplexity Trading Bot API Client
 * Integrated into main backend on port 8080
 * Uses dynamic URL to work with any frontend port
 */
const PERPLEXITY_API_BASE = window.location.protocol + '//' + window.location.hostname + ':8080/api/perplexity';

export interface ChatMessage {
	role: 'user' | 'assistant';
	content: string;
}

export interface Citation {
	title: string;
	url: string;
	snippet?: string;
}

export interface ChatRequest {
	message: string;
	image_data?: string;
	conversation_history?: ChatMessage[];
	model?: string;
	temperature?: number;
	max_tokens?: number;
}

export interface ChatResponse {
	success: boolean;
	message: string;
	citations: Citation[];
	related_questions: string[];
	model_used: string;
	tokens_used?: number;
	processing_time?: number;
	error?: string;
}

export interface HealthResponse {
	status: string;
	version: string;
	timestamp: string;
	perplexity_api_configured: boolean;
}

export interface ModelInfo {
	id: string;
	name: string;
	description: string;
	max_tokens: number;
}

export interface ModelsResponse {
	models: ModelInfo[];
	default_model: string;
}

class PerplexityAPI {
	private baseUrl: string;

	constructor(baseUrl: string = PERPLEXITY_API_BASE) {
		this.baseUrl = baseUrl;
	}

	async sendMessage(request: ChatRequest): Promise<ChatResponse> {
		try {
			const response = await fetch(`${this.baseUrl}/chat`, {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json'
				},
				body: JSON.stringify(request)
			});

			if (!response.ok) {
				throw new Error(`HTTP ${response.status}: ${response.statusText}`);
			}

			const data = await response.json();
			return data;
		} catch (error) {
			console.error('Perplexity API error:', error);
			throw error;
		}
	}

	async uploadImageForAnalysis(imageFile: File, message: string): Promise<ChatResponse> {
		try {
			// Convert image to base64
			const base64 = await this.fileToBase64(imageFile);
			
			return await this.sendMessage({
				message,
				image_data: base64
			});
		} catch (error) {
			console.error('Image upload error:', error);
			throw error;
		}
	}

	async getHealth(): Promise<HealthResponse> {
		try {
			const response = await fetch(`${this.baseUrl}/health`);
			
			if (!response.ok) {
				throw new Error(`HTTP ${response.status}: ${response.statusText}`);
			}

			return await response.json();
		} catch (error) {
			console.error('Health check error:', error);
			throw error;
		}
	}

	async getModels(): Promise<ModelsResponse> {
		try {
			const response = await fetch(`${this.baseUrl}/models`);
			
			if (!response.ok) {
				throw new Error(`HTTP ${response.status}: ${response.statusText}`);
			}

			return await response.json();
		} catch (error) {
			console.error('Get models error:', error);
			throw error;
		}
	}

	private fileToBase64(file: File): Promise<string> {
		return new Promise((resolve, reject) => {
			const reader = new FileReader();
			reader.readAsDataURL(file);
			reader.onload = () => {
				const result = reader.result as string;
				// Remove data:image/...;base64, prefix
				const base64 = result.split(',')[1];
				resolve(base64);
			};
			reader.onerror = error => reject(error);
		});
	}

	// Utility functions for parsing responses
	parseCitations(response: ChatResponse): Citation[] {
		return response.citations || [];
	}

	parseRelatedQuestions(response: ChatResponse): string[] {
		return response.related_questions || [];
	}

	formatProcessingTime(seconds?: number): string {
		if (!seconds) return 'N/A';
		return `${seconds.toFixed(2)}s`;
	}

	formatTokenUsage(tokens?: number): string {
		if (!tokens) return 'N/A';
		return `${tokens.toLocaleString()} tokens`;
	}
}

// Export singleton instance
export const perplexityAPI = new PerplexityAPI();

// Export class for custom instances
export { PerplexityAPI };
