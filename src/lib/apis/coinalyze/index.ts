/**
 * Coinalyze API Client
 * 
 * Provides access to crypto trading data including open interest, funding rates, and liquidations
 */

const API_BASE_URL = '';

export interface OpenInterestData {
	symbol: string;
	value: number;
	update: number;
}

export interface FundingRateData {
	symbol: string;
	value: number;
	update: number;
}

export interface LiquidationData {
	symbol: string;
	side: 'long' | 'short';
	value: number;
	timestamp: number;
}

export interface OHLCVData {
	timestamp: number;
	open: number;
	high: number;
	low: number;
	close: number;
	volume: number;
}

export interface MarketData {
	symbol: string;
	price: number;
	change24h: number;
	volume24h: number;
	openInterest: number;
	fundingRate: number;
	nextFunding: number;
}

/**
 * Get current open interest for symbols
 */
export const getOpenInterest = async (symbols: string[]): Promise<OpenInterestData[]> => {
	try {
		const symbolsParam = symbols.join(',');

		const response = await fetch(
			`${API_BASE_URL}/api/tradeberg/coinalyze/open-interest?symbols=${symbolsParam}`
		);

		if (!response.ok) {
			const errorData = await response.json().catch(() => ({}));
			throw new Error(errorData.detail || `Request failed: ${response.status}`);
		}

		const result: OpenInterestData[] = await response.json();
		return result;
	} catch (error) {
		console.error('❌ [Coinalyze] Error fetching open interest:', error);
		throw error;
	}
};

/**
 * Get current funding rates for symbols
 */
export const getFundingRates = async (symbols: string[]): Promise<FundingRateData[]> => {
	try {
		const symbolsParam = symbols.join(',');

		const response = await fetch(
			`${API_BASE_URL}/api/tradeberg/coinalyze/funding-rate?symbols=${symbolsParam}`
		);

		if (!response.ok) {
			const errorData = await response.json().catch(() => ({}));
			throw new Error(errorData.detail || `Request failed: ${response.status}`);
		}

		const result: FundingRateData[] = await response.json();
		return result;
	} catch (error) {
		console.error('❌ [Coinalyze] Error fetching funding rates:', error);
		throw error;
	}
};

/**
 * Get liquidation history
 */
export const getLiquidations = async (
	symbol: string,
	timeframe: string = '1h'
): Promise<LiquidationData[]> => {
	try {

		const response = await fetch(
			`${API_BASE_URL}/api/tradeberg/coinalyze/liquidations?symbol=${symbol}&timeframe=${timeframe}`
		);

		if (!response.ok) {
			const errorData = await response.json().catch(() => ({}));
			throw new Error(errorData.detail || `Request failed: ${response.status}`);
		}

		const result: LiquidationData[] = await response.json();
		return result;
	} catch (error) {
		console.error('❌ [Coinalyze] Error fetching liquidations:', error);
		throw error;
	}
};

/**
 * Get OHLCV data
 */
export const getOHLCV = async (
	symbol: string,
	timeframe: string = '1h',
	limit: number = 100
): Promise<OHLCVData[]> => {
	try {

		const response = await fetch(
			`${API_BASE_URL}/api/coinalyze/ohlcv?symbol=${symbol}&timeframe=${timeframe}&limit=${limit}`
		);

		if (!response.ok) {
			const errorData = await response.json().catch(() => ({}));
			throw new Error(errorData.detail || `Request failed: ${response.status}`);
		}

		const result: OHLCVData[] = await response.json();
		return result;
	} catch (error) {
		console.error('❌ [Coinalyze] Error fetching OHLCV:', error);
		throw error;
	}
};

/**
 * Get comprehensive market data for a symbol
 */
export const getMarketData = async (symbol: string): Promise<MarketData> => {
	try {

		const [openInterest, fundingRate] = await Promise.all([
			getOpenInterest([symbol]),
			getFundingRates([symbol])
		]);

		// Mock additional data that would come from other endpoints
		const marketData: MarketData = {
			symbol,
			price: 0, // Would come from price endpoint
			change24h: 0, // Would come from price endpoint
			volume24h: 0, // Would come from volume endpoint
			openInterest: openInterest[0]?.value || 0,
			fundingRate: fundingRate[0]?.value || 0,
			nextFunding: Date.now() + 8 * 60 * 60 * 1000 // 8 hours from now
		};

		return marketData;
	} catch (error) {
		console.error('❌ [Coinalyze] Error fetching market data:', error);
		throw error;
	}
};

/**
 * Check Coinalyze API health
 */
export const checkCoinalyzeHealth = async (): Promise<{ configured: boolean; api_base_url: string }> => {
	try {
		const response = await fetch(`${API_BASE_URL}/api/tradeberg/coinalyze/health`);
		return await response.json();
	} catch (error) {
		console.error('❌ [Coinalyze] Health check failed:', error);
		return { configured: false, api_base_url: '' };
	}
};
