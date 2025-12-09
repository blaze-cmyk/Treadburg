/**
 * API Client for TradeBerg Backend
 * Handles all communication with the FastAPI backend
 * ALL requests go through backend - no direct Supabase/Stripe calls from frontend
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'https://treadburg.onrender.com';

// Store auth token
let authToken: string | null = null;

export function setAuthToken(token: string | null) {
  authToken = token;
  if (token) {
    localStorage.setItem('auth_token', token);
    // Also set as cookie for middleware access
    document.cookie = `auth_token=${token}; path=/; max-age=${60 * 60 * 24 * 7}`; // 7 days
  } else {
    localStorage.removeItem('auth_token');
    // Remove cookie
    document.cookie = 'auth_token=; path=/; max-age=0';
  }
}

export function getAuthToken(): string | null {
  if (!authToken && typeof window !== 'undefined') {
    authToken = localStorage.getItem('auth_token');
  }
  return authToken;
}

interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  timestamp?: string;
}

interface ChatRequest {
  message: string;
  chat_id?: string;
  user_id?: string;
}

interface ChatResponse {
  response: string;
  chat_id: string;
  sources?: any[];
}

/**
 * Send a chat message to the backend
 */
export async function sendChatMessage(
  message: string,
  chatId?: string,
  userId?: string
): Promise<ChatResponse> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        message,
        chat_id: chatId,
        user_id: userId,
      }),
    });

    if (!response.ok) {
      throw new Error(`API Error: ${response.status} ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error sending chat message:', error);
    throw error;
  }
}

/**
 * Stream chat response from backend
 */
export async function streamChatMessage(
  message: string,
  chatId?: string,
  userId?: string,
  onChunk?: (chunk: string) => void
): Promise<string> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/chat/stream`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        message,
        chat_id: chatId,
        user_id: userId,
      }),
    });

    if (!response.ok) {
      throw new Error(`API Error: ${response.status} ${response.statusText}`);
    }

    const reader = response.body?.getReader();
    const decoder = new TextDecoder();
    let fullResponse = '';

    if (!reader) {
      throw new Error('No response body');
    }

    while (true) {
      const { done, value } = await reader.read();
      
      if (done) break;
      
      const chunk = decoder.decode(value, { stream: true });
      fullResponse += chunk;
      
      if (onChunk) {
        onChunk(chunk);
      }
    }

    return fullResponse;
  } catch (error) {
    console.error('Error streaming chat message:', error);
    throw error;
  }
}

/**
 * Get chat history for a user
 */
export async function getChatHistory(userId: string): Promise<any[]> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/chat/history/${userId}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`API Error: ${response.status} ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error fetching chat history:', error);
    throw error;
  }
}

/**
 * Get specific chat by ID
 */
export async function getChat(chatId: string): Promise<any> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/chat/${chatId}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`API Error: ${response.status} ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error fetching chat:', error);
    throw error;
  }
}

/**
 * Delete a chat
 */
export async function deleteChat(chatId: string): Promise<void> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/chat/${chatId}`, {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`API Error: ${response.status} ${response.statusText}`);
    }
  } catch (error) {
    console.error('Error deleting chat:', error);
    throw error;
  }
}

/**
 * Get trading data
 */
export async function getTradingData(symbol: string): Promise<any> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/trading/${symbol}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`API Error: ${response.status} ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error fetching trading data:', error);
    throw error;
  }
}

/**
 * Health check
 */
export async function healthCheck(): Promise<boolean> {
  try {
    const response = await fetch(`${API_BASE_URL}/health`, {
      method: 'GET',
    });

    return response.ok;
  } catch (error) {
    console.error('Backend health check failed:', error);
    return false;
  }
}

/**
 * Authentication APIs
 */
export async function login(email: string, password: string): Promise<any> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ email, password }),
    });

    if (!response.ok) {
      throw new Error(`Login failed: ${response.status}`);
    }

    const data = await response.json();
    
    if (data.access_token) {
      setAuthToken(data.access_token);
    }
    
    return data;
  } catch (error) {
    console.error('Login error:', error);
    throw error;
  }
}

export async function register(email: string, password: string, fullName?: string): Promise<any> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/auth/register`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ 
        email, 
        password,
        full_name: fullName 
      }),
    });

    if (!response.ok) {
      throw new Error(`Registration failed: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Registration error:', error);
    throw error;
  }
}

export async function logout(): Promise<void> {
  try {
    const token = getAuthToken();
    
    await fetch(`${API_BASE_URL}/api/auth/logout`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(token && { 'Authorization': `Bearer ${token}` }),
      },
    });
    
    setAuthToken(null);
  } catch (error) {
    console.error('Logout error:', error);
    setAuthToken(null);
  }
}

export async function getCurrentUser(): Promise<any> {
  try {
    const token = getAuthToken();
    
    const response = await fetch(`${API_BASE_URL}/api/auth/me`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        ...(token && { 'Authorization': `Bearer ${token}` }),
      },
    });

    if (!response.ok) {
      throw new Error(`Failed to get user: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Get user error:', error);
    throw error;
  }
}

export async function updateUserProfile(updates: any): Promise<any> {
  try {
    const token = getAuthToken();
    
    const response = await fetch(`${API_BASE_URL}/api/auth/profile`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        ...(token && { 'Authorization': `Bearer ${token}` }),
      },
      body: JSON.stringify(updates),
    });

    if (!response.ok) {
      throw new Error(`Failed to update profile: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Update profile error:', error);
    throw error;
  }
}

export async function resetPassword(email: string): Promise<any> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/auth/reset-password`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ email }),
    });

    if (!response.ok) {
      throw new Error(`Failed to reset password: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Reset password error:', error);
    throw error;
  }
}

export async function updatePassword(newPassword: string): Promise<any> {
  try {
    const token = getAuthToken();
    
    const response = await fetch(`${API_BASE_URL}/api/auth/update-password`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(token && { 'Authorization': `Bearer ${token}` }),
      },
      body: JSON.stringify({ new_password: newPassword }),
    });

    if (!response.ok) {
      throw new Error(`Failed to update password: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Update password error:', error);
    throw error;
  }
}

/**
 * Billing/Stripe APIs
 */
export async function getSubscriptionTiers(): Promise<any[]> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/billing/tiers`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`Failed to get tiers: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Get tiers error:', error);
    throw error;
  }
}

export async function createCheckoutSession(priceId: string, customerEmail?: string): Promise<any> {
  try {
    const token = getAuthToken();
    
    const response = await fetch(`${API_BASE_URL}/api/billing/create-checkout-session`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(token && { 'Authorization': `Bearer ${token}` }),
      },
      body: JSON.stringify({
        price_id: priceId,
        mode: 'subscription',
        customer_email: customerEmail,
      }),
    });

    if (!response.ok) {
      throw new Error(`Failed to create checkout: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Create checkout error:', error);
    throw error;
  }
}

export async function getUserCredits(): Promise<number> {
  try {
    const token = getAuthToken();
    
    const response = await fetch(`${API_BASE_URL}/api/billing/credits`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        ...(token && { 'Authorization': `Bearer ${token}` }),
      },
    });

    if (!response.ok) {
      throw new Error(`Failed to get credits: ${response.status}`);
    }

    const data = await response.json();
    return data.credits || 0;
  } catch (error) {
    console.error('Get credits error:', error);
    return 0;
  }
}

export async function getUserSubscription(): Promise<any> {
  try {
    const token = getAuthToken();
    
    const response = await fetch(`${API_BASE_URL}/api/billing/subscription`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        ...(token && { 'Authorization': `Bearer ${token}` }),
      },
    });

    if (!response.ok) {
      throw new Error(`Failed to get subscription: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Get subscription error:', error);
    throw error;
  }
}

export const apiClient = {
  // Auth
  login,
  register,
  logout,
  getCurrentUser,
  updateUserProfile,
  resetPassword,
  updatePassword,
  setAuthToken,
  getAuthToken,
  
  // Chat
  sendChatMessage,
  streamChatMessage,
  getChatHistory,
  getChat,
  deleteChat,
  
  // Trading
  getTradingData,
  
  // Billing/Stripe
  getSubscriptionTiers,
  createCheckoutSession,
  getUserCredits,
  getUserSubscription,
  
  // Health
  healthCheck,
};
