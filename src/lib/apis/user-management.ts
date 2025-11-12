/**
 * User Management API Client
 * Handles user profiles, credits, payments, and subscriptions
 */

const API_BASE = '/api/user-management';

// Types
export interface UserProfile {
	id: string;
	email: string;
	username?: string;
	full_name?: string;
	avatar_url?: string;
	bio?: string;
	credits: number;
	total_credits_purchased: number;
	total_credits_used: number;
	subscription_tier: 'free' | 'basic' | 'pro' | 'enterprise';
	subscription_status: 'active' | 'inactive' | 'cancelled' | 'expired';
	is_verified: boolean;
	created_at: string;
	last_login_at?: string;
}

export interface UserStats {
	total_credits_purchased: number;
	total_credits_used: number;
	current_credits: number;
	total_payments: number;
	total_spent: number;
	api_calls_count: number;
	login_count: number;
	last_login?: string;
	member_since: string;
}

export interface CreditTransaction {
	id: string;
	transaction_type: 'purchase' | 'usage' | 'refund' | 'bonus' | 'admin_adjustment';
	amount: number;
	balance_after: number;
	description?: string;
	created_at: string;
}

export interface Payment {
	id: string;
	amount: number;
	credits_purchased: number;
	status: 'pending' | 'succeeded' | 'failed' | 'refunded' | 'cancelled';
	stripe_payment_intent_id?: string;
	created_at: string;
	paid_at?: string;
}

// API Functions

/**
 * Get current user profile with stats
 */
export async function getUserProfile(token: string): Promise<{ user: UserProfile; stats: UserStats }> {
	const response = await fetch(`${API_BASE}/profile`, {
		headers: {
			'Authorization': `Bearer ${token}`
		}
	});
	
	if (!response.ok) {
		throw new Error(`Failed to fetch profile: ${response.statusText}`);
	}
	
	return response.json();
}

/**
 * Update user profile
 */
export async function updateUserProfile(
	token: string,
	data: {
		username?: string;
		full_name?: string;
		avatar_url?: string;
		bio?: string;
	}
): Promise<{ success: boolean; user: UserProfile }> {
	const response = await fetch(`${API_BASE}/profile`, {
		method: 'PUT',
		headers: {
			'Authorization': `Bearer ${token}`,
			'Content-Type': 'application/json'
		},
		body: JSON.stringify(data)
	});
	
	if (!response.ok) {
		throw new Error(`Failed to update profile: ${response.statusText}`);
	}
	
	return response.json();
}

/**
 * Get user credits
 */
export async function getUserCredits(token: string): Promise<{
	success: boolean;
	credits: number;
	total_purchased: number;
	total_used: number;
}> {
	const response = await fetch(`${API_BASE}/credits`, {
		headers: {
			'Authorization': `Bearer ${token}`
		}
	});
	
	if (!response.ok) {
		throw new Error(`Failed to fetch credits: ${response.statusText}`);
	}
	
	return response.json();
}

/**
 * Purchase credits - creates Stripe checkout session
 */
export async function purchaseCredits(
	token: string,
	data: {
		amount: number;
		credits: number;
		success_url: string;
		cancel_url: string;
	}
): Promise<{
	success: boolean;
	checkout_url: string;
	session_id: string;
	payment_id: string;
}> {
	const response = await fetch(`${API_BASE}/credits/purchase`, {
		method: 'POST',
		headers: {
			'Authorization': `Bearer ${token}`,
			'Content-Type': 'application/json'
		},
		body: JSON.stringify(data)
	});
	
	if (!response.ok) {
		throw new Error(`Failed to create checkout: ${response.statusText}`);
	}
	
	return response.json();
}

/**
 * Use credits (deduct from balance)
 */
export async function useCredits(
	token: string,
	data: {
		credits: number;
		description: string;
		endpoint?: string;
	}
): Promise<{
	success: boolean;
	credits_used: number;
	new_balance: number;
}> {
	const response = await fetch(`${API_BASE}/credits/use`, {
		method: 'POST',
		headers: {
			'Authorization': `Bearer ${token}`,
			'Content-Type': 'application/json'
		},
		body: JSON.stringify(data)
	});
	
	if (!response.ok) {
		const error = await response.json();
		throw new Error(error.detail || 'Failed to use credits');
	}
	
	return response.json();
}

/**
 * Get credit transaction history
 */
export async function getCreditTransactions(
	token: string,
	limit: number = 50
): Promise<{
	success: boolean;
	transactions: CreditTransaction[];
}> {
	const response = await fetch(`${API_BASE}/credits/transactions?limit=${limit}`, {
		headers: {
			'Authorization': `Bearer ${token}`
		}
	});
	
	if (!response.ok) {
		throw new Error(`Failed to fetch transactions: ${response.statusText}`);
	}
	
	return response.json();
}

/**
 * Get payment history
 */
export async function getPayments(
	token: string,
	limit: number = 50
): Promise<{
	success: boolean;
	payments: Payment[];
}> {
	const response = await fetch(`${API_BASE}/payments?limit=${limit}`, {
		headers: {
			'Authorization': `Bearer ${token}`
		}
	});
	
	if (!response.ok) {
		throw new Error(`Failed to fetch payments: ${response.statusText}`);
	}
	
	return response.json();
}

/**
 * Get subscription details
 */
export async function getSubscription(token: string): Promise<{
	success: boolean;
	subscription: any;
	tier: string;
	status: string;
}> {
	const response = await fetch(`${API_BASE}/subscription`, {
		headers: {
			'Authorization': `Bearer ${token}`
		}
	});
	
	if (!response.ok) {
		throw new Error(`Failed to fetch subscription: ${response.statusText}`);
	}
	
	return response.json();
}
