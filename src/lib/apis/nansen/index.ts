/**
 * Nansen API Client
 * 
 * Provides access to Nansen's DeFi and smart money data
 */

const API_BASE_URL = '';

export interface DeFiHolding {
	token_address: string;
	token_name: string;
	token_symbol: string;
	balance: string;
	value_usd: number;
	chain: string;
	protocol?: string;
}

export interface DeFiHoldingsRequest {
	wallet_address: string;
}

export interface DeFiHoldingsResponse {
	success: boolean;
	wallet_address: string;
	data: {
		holdings: DeFiHolding[];
		total_value_usd: number;
		chains: string[];
	};
}

export interface SmartMoneyRequest {
	chains?: string[];
	page?: number;
	per_page?: number;
	order_by?: string;
}

export interface SmartMoneyHolding {
	token_address: string;
	token_name: string;
	token_symbol: string;
	holders_count: number;
	total_value_usd: number;
	chain: string;
}

export interface SmartMoneyResponse {
	success: boolean;
	data: {
		holdings: SmartMoneyHolding[];
		pagination: {
			page: number;
			per_page: number;
			total: number;
		};
	};
}

/**
 * Get DeFi holdings for a wallet address
 */
export const getDeFiHoldings = async (
	request: DeFiHoldingsRequest,
	token?: string
): Promise<DeFiHoldingsResponse> => {
	try {

		const headers: HeadersInit = {
			'Content-Type': 'application/json'
		};

		if (token) {
			headers['Authorization'] = `Bearer ${token}`;
		}

		const response = await fetch(`${API_BASE_URL}/api/tradeberg/defi-holdings`, {
			method: 'POST',
			headers,
			body: JSON.stringify(request)
		});

		if (!response.ok) {
			const errorData = await response.json().catch(() => ({}));
			throw new Error(errorData.detail || `Request failed: ${response.status}`);
		}

		const result: DeFiHoldingsResponse = await response.json();
		return result;
	} catch (error) {
		console.error('❌ [Nansen] Error fetching DeFi holdings:', error);
		throw error;
	}
};

/**
 * Get smart money holdings across chains
 */
export const getSmartMoneyHoldings = async (
	request: SmartMoneyRequest = {},
	token?: string
): Promise<SmartMoneyResponse> => {
	try {

		const headers: HeadersInit = {
			'Content-Type': 'application/json'
		};

		if (token) {
			headers['Authorization'] = `Bearer ${token}`;
		}

		const response = await fetch(`${API_BASE_URL}/api/nansen/smart-money/holdings`, {
			method: 'POST',
			headers,
			body: JSON.stringify({
				chains: request.chains || ['ethereum', 'solana', 'base'],
				page: request.page || 1,
				per_page: request.per_page || 50,
				order_by: request.order_by || 'value_usd'
			})
		});

		if (!response.ok) {
			const errorData = await response.json().catch(() => ({}));
			throw new Error(errorData.detail || `Request failed: ${response.status}`);
		}

		const result: SmartMoneyResponse = await response.json();
		return result;
	} catch (error) {
		console.error('❌ [Nansen] Error fetching smart money holdings:', error);
		throw error;
	}
};

/**
 * Check Nansen API health
 */
export const checkNansenHealth = async (): Promise<{ configured: boolean; api_base_url: string }> => {
	try {
		const response = await fetch(`${API_BASE_URL}/api/nansen/health`);
		return await response.json();
	} catch (error) {
		console.error('❌ [Nansen] Health check failed:', error);
		return { configured: false, api_base_url: '' };
	}
};
