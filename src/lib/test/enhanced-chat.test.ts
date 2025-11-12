/**
 * Frontend Test Suite for Enhanced Perplexity Chat System
 * Tests TypeScript API client, response parsing, and UI integration
 */

import { describe, it, expect, beforeEach, vi, type Mock } from 'vitest';
import {
	sendPerplexityChat,
	sendSmartChat,
	parseRelatedQuestions,
	parseCitations,
	uploadImageForAnalysis,
	needsMarketData,
	ENHANCED_ANALYSIS_TEMPLATES,
	type EnhancedChatResponse,
	type Citation
} from '../apis/tradeberg/enhanced-chat';

// Mock fetch globally
global.fetch = vi.fn();

describe('Enhanced Perplexity Chat API', () => {
	beforeEach(() => {
		vi.clearAllMocks();
	});

	describe('sendPerplexityChat', () => {
		it('should send text-only message successfully', async () => {
			const mockResponse = {
				ok: true,
				json: vi.fn().mockResolvedValue({
					choices: [
						{
							message: {
								content: 'Bitcoin is showing bullish momentum with key support at $65,000.'
							}
						}
					],
					usage: { total_tokens: 150 },
					model: 'sonar-pro'
				})
			};

			(fetch as Mock).mockResolvedValue(mockResponse);

			const result = await sendPerplexityChat('Analyze Bitcoin price action');

			expect(result.success).toBe(true);
			expect(result.response).toContain('Bitcoin is showing bullish momentum');
			expect(result.usage?.total_tokens).toBe(150);
			expect(result.model).toBe('sonar-pro');
		});

		it('should send message with image data', async () => {
			const mockResponse = {
				ok: true,
				json: vi.fn().mockResolvedValue({
					choices: [
						{
							message: {
								content: 'Chart analysis: Clear breakout pattern above resistance at $66,000.'
							}
						}
					],
					usage: { total_tokens: 200 }
				})
			};

			(fetch as Mock).mockResolvedValue(mockResponse);

			const imageData = 'base64encodedimagedata';
			const result = await sendPerplexityChat('Analyze this chart', 'session_123', imageData);

			expect(result.success).toBe(true);
			expect(result.response).toContain('Chart analysis');

			// Verify fetch was called with correct payload
			const fetchCall = (fetch as Mock).mock.calls[0];
			const requestBody = JSON.parse(fetchCall[1].body);
			
			expect(requestBody.messages[0].content).toEqual([
				{ type: 'text', text: 'Analyze this chart' },
				{ type: 'image_url', image_url: { url: 'data:image/png;base64,base64encodedimagedata' } }
			]);
		});

		it('should handle API errors gracefully', async () => {
			const mockResponse = {
				ok: false,
				status: 400,
				json: vi.fn().mockResolvedValue({
					detail: 'Bad Request: Invalid parameters'
				})
			};

			(fetch as Mock).mockResolvedValue(mockResponse);

			const result = await sendPerplexityChat('Test query');

			expect(result.success).toBe(false);
			expect(result.error).toContain('Bad Request: Invalid parameters');
			expect(result.response).toContain('I apologize, but I encountered an error');
		});

		it('should handle network errors', async () => {
			(fetch as Mock).mockRejectedValue(new Error('Network error'));

			const result = await sendPerplexityChat('Test query');

			expect(result.success).toBe(false);
			expect(result.error).toBe('Network error');
		});
	});

	describe('sendSmartChat', () => {
		it('should delegate to sendPerplexityChat', async () => {
			const mockResponse = {
				ok: true,
				json: vi.fn().mockResolvedValue({
					choices: [{ message: { content: 'Smart response' } }],
					usage: { total_tokens: 100 }
				})
			};

			(fetch as Mock).mockResolvedValue(mockResponse);

			const result = await sendSmartChat('Test query');

			expect(result.success).toBe(true);
			expect(result.response).toBe('Smart response');
		});
	});
});

describe('Response Parsing Functions', () => {
	describe('parseRelatedQuestions', () => {
		it('should extract related questions from response', () => {
			const response = `
## Market Analysis

Bitcoin shows strong momentum.

## 💡 Related Questions

- 🔍 **What about Ethereum price action?**
- 🔍 **Key resistance levels for BTC?**
- 🔍 **DeFi impact on market sentiment?**

## Summary
			`;

			const questions = parseRelatedQuestions(response);

			expect(questions).toHaveLength(3);
			expect(questions[0]).toBe('What about Ethereum price action?');
			expect(questions[1]).toBe('Key resistance levels for BTC?');
			expect(questions[2]).toBe('DeFi impact on market sentiment?');
		});

		it('should handle response without related questions', () => {
			const response = 'Simple response without questions.';
			const questions = parseRelatedQuestions(response);
			expect(questions).toHaveLength(0);
		});

		it('should handle alternative question formats', () => {
			const response = `
## 💡 Related Questions

- **What is the current trend?**
- **How does this affect altcoins?**
			`;

			const questions = parseRelatedQuestions(response);

			expect(questions).toHaveLength(2);
			expect(questions[0]).toBe('What is the current trend?');
			expect(questions[1]).toBe('How does this affect altcoins?');
		});
	});

	describe('parseCitations', () => {
		it('should extract citations from response', () => {
			const response = `
## Analysis

Market data shows positive trends.

## 📚 Sources & Citations

1. **[CoinDesk Bitcoin Analysis](https://coindesk.com/bitcoin-analysis)**
2. **[CoinTelegraph Market Report](https://cointelegraph.com/market-report)**
3. **[Binance Research](https://research.binance.com/analysis)**

## Summary
			`;

			const citations = parseCitations(response);

			expect(citations).toHaveLength(3);
			expect(citations[0]).toEqual({
				title: 'CoinDesk Bitcoin Analysis',
				url: 'https://coindesk.com/bitcoin-analysis'
			});
			expect(citations[1]).toEqual({
				title: 'CoinTelegraph Market Report',
				url: 'https://cointelegraph.com/market-report'
			});
		});

		it('should handle response without citations', () => {
			const response = 'Response without any citations.';
			const citations = parseCitations(response);
			expect(citations).toHaveLength(0);
		});
	});
});

describe('Image Upload Functionality', () => {
	it('should convert file to base64 and send for analysis', async () => {
		// Mock FileReader
		const mockFileReader = {
			readAsDataURL: vi.fn(),
			onload: null as any,
			onerror: null as any,
			result: 'data:image/png;base64,mockbase64data'
		};

		global.FileReader = vi.fn(() => mockFileReader) as any;

		// Mock successful API response
		const mockResponse = {
			ok: true,
			json: vi.fn().mockResolvedValue({
				choices: [{ message: { content: 'Chart shows bullish pattern' } }],
				usage: { total_tokens: 180 }
			})
		};

		(fetch as Mock).mockResolvedValue(mockResponse);

		// Create mock file
		const mockFile = new File(['mock image data'], 'chart.png', { type: 'image/png' });

		// Start the upload
		const uploadPromise = uploadImageForAnalysis(mockFile, 'Analyze this chart');

		// Simulate FileReader success
		setTimeout(() => {
			mockFileReader.onload();
		}, 0);

		const result = await uploadPromise;

		expect(result.success).toBe(true);
		expect(result.response).toContain('Chart shows bullish pattern');
		expect(mockFileReader.readAsDataURL).toHaveBeenCalledWith(mockFile);
	});

	it('should handle file reading errors', async () => {
		const mockFileReader = {
			readAsDataURL: vi.fn(),
			onload: null as any,
			onerror: null as any
		};

		global.FileReader = vi.fn(() => mockFileReader) as any;

		const mockFile = new File(['mock data'], 'chart.png', { type: 'image/png' });

		const uploadPromise = uploadImageForAnalysis(mockFile, 'Analyze chart');

		// Simulate FileReader error
		setTimeout(() => {
			mockFileReader.onerror(new Error('File read error'));
		}, 0);

		const result = await uploadPromise;

		expect(result.success).toBe(false);
		expect(result.error).toContain('File read error');
	});
});

describe('Utility Functions', () => {
	describe('needsMarketData', () => {
		it('should detect queries that need market data', () => {
			const testCases = [
				{ query: 'BTC open interest analysis', expected: true },
				{ query: 'Ethereum funding rates', expected: true },
				{ query: 'Bitcoin liquidation data', expected: true },
				{ query: 'DeFi wallet analysis', expected: true },
				{ query: 'market structure for USDT pairs', expected: true },
				{ query: 'Hello world', expected: false },
				{ query: 'How are you?', expected: false }
			];

			testCases.forEach(({ query, expected }) => {
				expect(needsMarketData(query)).toBe(expected);
			});
		});
	});

	describe('ENHANCED_ANALYSIS_TEMPLATES', () => {
		it('should provide predefined analysis templates', () => {
			expect(ENHANCED_ANALYSIS_TEMPLATES.btc_analysis).toContain('Bitcoin');
			expect(ENHANCED_ANALYSIS_TEMPLATES.eth_analysis).toContain('Ethereum');
			expect(ENHANCED_ANALYSIS_TEMPLATES.market_overview).toContain('market overview');
			expect(ENHANCED_ANALYSIS_TEMPLATES.chart_analysis).toContain('chart');
			expect(ENHANCED_ANALYSIS_TEMPLATES.defi_analysis).toContain('DeFi');
		});
	});
});

describe('Integration Tests', () => {
	it('should handle complete chat flow with all features', async () => {
		const mockResponse = {
			ok: true,
			json: vi.fn().mockResolvedValue({
				choices: [
					{
						message: {
							content: `
## 📊 Market Analysis

Bitcoin shows strong bullish momentum with key support at $65,000.

## 💡 Related Questions

- 🔍 **What about Ethereum performance?**
- 🔍 **Key resistance levels to watch?**

## 📚 Sources & Citations

1. **[CoinDesk Analysis](https://coindesk.com/analysis)**
2. **[Binance Research](https://research.binance.com)**
							`
						}
					}
				],
				usage: { total_tokens: 250 },
				model: 'sonar-pro'
			})
		};

		(fetch as Mock).mockResolvedValue(mockResponse);

		const result = await sendPerplexityChat('Comprehensive Bitcoin analysis');

		expect(result.success).toBe(true);
		expect(result.response).toContain('Market Analysis');
		expect(result.usage?.total_tokens).toBe(250);

		// Test parsing functions on the response
		const questions = parseRelatedQuestions(result.response);
		const citations = parseCitations(result.response);

		expect(questions).toHaveLength(2);
		expect(citations).toHaveLength(2);
		expect(questions[0]).toBe('What about Ethereum performance?');
		expect(citations[0].title).toBe('CoinDesk Analysis');
	});

	it('should handle session management', async () => {
		const mockResponse = {
			ok: true,
			json: vi.fn().mockResolvedValue({
				choices: [{ message: { content: 'Session response' } }],
				usage: { total_tokens: 100 }
			})
		};

		(fetch as Mock).mockResolvedValue(mockResponse);

		const sessionId = 'test_session_123';
		const result = await sendPerplexityChat('Test message', sessionId);

		expect(result.success).toBe(true);

		// Verify session ID was included in request
		const fetchCall = (fetch as Mock).mock.calls[0];
		const requestBody = JSON.parse(fetchCall[1].body);
		expect(requestBody.session_id).toBe(sessionId);
	});
});

describe('Error Handling and Edge Cases', () => {
	it('should handle empty responses', async () => {
		const mockResponse = {
			ok: true,
			json: vi.fn().mockResolvedValue({
				choices: [{ message: { content: '' } }],
				usage: { total_tokens: 0 }
			})
		};

		(fetch as Mock).mockResolvedValue(mockResponse);

		const result = await sendPerplexityChat('Test query');

		expect(result.success).toBe(true);
		expect(result.response).toBe('');
	});

	it('should handle malformed API responses', async () => {
		const mockResponse = {
			ok: true,
			json: vi.fn().mockResolvedValue({
				// Missing choices array
				usage: { total_tokens: 0 }
			})
		};

		(fetch as Mock).mockResolvedValue(mockResponse);

		const result = await sendPerplexityChat('Test query');

		expect(result.success).toBe(true);
		expect(result.response).toBe(''); // Should handle gracefully
	});

	it('should handle JSON parsing errors', async () => {
		const mockResponse = {
			ok: true,
			json: vi.fn().mockRejectedValue(new Error('Invalid JSON'))
		};

		(fetch as Mock).mockResolvedValue(mockResponse);

		const result = await sendPerplexityChat('Test query');

		expect(result.success).toBe(false);
		expect(result.error).toBe('Invalid JSON');
	});
});

describe('Performance Tests', () => {
	it('should handle concurrent requests', async () => {
		const mockResponse = {
			ok: true,
			json: vi.fn().mockResolvedValue({
				choices: [{ message: { content: 'Concurrent response' } }],
				usage: { total_tokens: 100 }
			})
		};

		(fetch as Mock).mockResolvedValue(mockResponse);

		// Send 5 concurrent requests
		const promises = Array.from({ length: 5 }, (_, i) => 
			sendPerplexityChat(`Query ${i}`, `session_${i}`)
		);

		const results = await Promise.all(promises);

		// All should succeed
		results.forEach((result, i) => {
			expect(result.success).toBe(true);
			expect(result.response).toBe('Concurrent response');
		});

		// Verify all requests were made
		expect(fetch).toHaveBeenCalledTimes(5);
	});

	it('should handle large responses', () => {
		const largeResponse = 'A'.repeat(50000); // 50KB response
		const questions = parseRelatedQuestions(largeResponse);
		const citations = parseCitations(largeResponse);

		// Should handle large content without issues
		expect(questions).toBeInstanceOf(Array);
		expect(citations).toBeInstanceOf(Array);
	});
});

// Mock console methods to avoid test noise
console.error = vi.fn();
console.log = vi.fn();
