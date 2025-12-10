/**
 * Backend API Client
 * Centralized service for communicating with FastAPI backend
 */

// NOTE:
// - All frontend calls should go through Next.js API routes on the same origin
//   (e.g. `/api/chat/...`) to avoid browser CORS issues.
// - Those Next routes proxy to the FastAPI backend (`http://localhost:8080/api`).
// - So here we keep `API_BASE_URL` empty and always pass absolute paths like `/api/...`.
const API_BASE_URL = "";

interface ApiResponse<T = any> {
  data?: T;
  error?: string;
  status: number;
}

/**
 * Generic fetch wrapper with error handling
 */
async function apiFetch<T = any>(
  endpoint: string,
  options: RequestInit = {}
): Promise<ApiResponse<T>> {
  try {
    const url = `${API_BASE_URL}${endpoint}`;

    const response = await fetch(url, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      return {
        error: errorData.detail || errorData.error || `HTTP ${response.status}`,
        status: response.status,
      };
    }

    // Handle streaming responses
    if (response.headers.get('content-type')?.includes('text/plain')) {
      return {
        data: response as any,
        status: response.status,
      };
    }

    const data = await response.json();
    return {
      data,
      status: response.status,
    };
  } catch (error) {
    console.error('API fetch error:', error);
    return {
      error: error instanceof Error ? error.message : 'Network error',
      status: 500,
    };
  }
}

/**
 * Chat API endpoints
 */
export const chatApi = {
  /**
   * Get all chats
   */
  async getAllChats() {
    return apiFetch("/api/chat");
  },

  /**
   * Create a new chat
   */
  async createChat(prompt: string) {
    return apiFetch("/api/chat/create", {
      method: "POST",
      body: JSON.stringify({ prompt }),
    });
  },

  /**
   * Get chat by ID
   */
  async getChat(chatId: string) {
    return apiFetch(`/api/chat/${chatId}`);
  },

  /**
   * Get messages for a chat
   */
  async getMessages(chatId: string) {
    // Next.js route: /api/chat/[chatId]/message -> proxies to backend /chat/{id}/messages
    return apiFetch(`/api/chat/${chatId}/message`);
  },

  /**
   * Stream chat response
   */
  async streamMessage(
    chatId: string,
    userPrompt: string,
    attachments?: { type: string; data: string }[],
    signal?: AbortSignal,
    mode?: string // "chat" or "trade"
  ) {
    // Use Next.js streaming route: /api/chat/[chatId]/message (POST)
    const url = `/api/chat/${chatId}/message`;

    const response = await fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ userPrompt, attachments, mode }),
      signal,
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }

    return response;
  },

  /**
   * Get token limit
   */
  async getTokenLimit() {
    return apiFetch("/api/chat/limit");
  },
};

/**
 * Auth API endpoints
 */
export const authApi = {
  async login(email: string, password: string) {
    return apiFetch('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });
  },

  async register(email: string, password: string, username?: string) {
    return apiFetch('/auth/register', {
      method: 'POST',
      body: JSON.stringify({ email, password, username }),
    });
  },

  async logout() {
    return apiFetch('/auth/logout', {
      method: 'POST',
    });
  },

  async getCurrentUser() {
    return apiFetch('/auth/me');
  },
};

/**
 * User API endpoints
 */
export const userApi = {
  async getProfile() {
    return apiFetch('/users/profile');
  },

  async updateProfile(data: any) {
    return apiFetch('/users/profile', {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  },

  async getCredits() {
    return apiFetch('/users/credits');
  },
};

/**
 * Trading API endpoints
 */
export const tradingApi = {
  async getTradingHistory(params?: { symbol?: string; startDate?: string; endDate?: string }) {
    const queryParams = new URLSearchParams(params as any).toString();
    return apiFetch(`/trading/history${queryParams ? `?${queryParams}` : ''}`);
  },

  async getZones(symbol: string, timeframe?: string) {
    const params = new URLSearchParams({ symbol, ...(timeframe && { timeframe }) });
    return apiFetch(`/trading/zones?${params}`);
  },

  async addTradingHistory(data: any) {
    return apiFetch('/trading/history', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },
};

/**
 * Integration API endpoints
 */
export const integrationApi = {
  async healthCheck() {
    return apiFetch('/integrations/health');
  },

  async supabaseStatus() {
    return apiFetch('/integrations/supabase/status');
  },

  async stripeStatus() {
    return apiFetch('/integrations/stripe/status');
  },
};

/**
 * Health check for backend
 */
export async function checkBackendHealth() {
  try {
    const response = await fetch(`${API_BASE_URL.replace('/api', '')}/health`);
    return response.ok;
  } catch {
    return false;
  }
}

export default {
  chatApi,
  authApi,
  userApi,
  tradingApi,
  integrationApi,
  checkBackendHealth,
};
