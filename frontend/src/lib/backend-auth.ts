/**
 * Backend Auth Helpers
 * All auth operations go through backend API
 */

export interface AuthResponse {
    success: boolean;
    access_token?: string;
    refresh_token?: string;
    user?: {
        id: string;
        email: string;
        full_name?: string;
        subscription_tier?: string;
        credits?: number;
    };
    message?: string;
}

export const backendAuth = {
    /**
     * Sign up with email and password
     */
    async signup(email: string, password: string, fullName?: string): Promise<AuthResponse> {
        const response = await fetch('/api/auth/signup', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password, full_name: fullName }),
        });

        return response.json();
    },

    /**
     * Login with email and password
     */
    async login(email: string, password: string): Promise<AuthResponse> {
        const response = await fetch('/api/auth/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password }),
        });

        return response.json();
    },

    /**
     * Initialize Google OAuth flow
     */
    async googleInit(redirectUrl: string = `${window.location.origin}/api/auth/google/callback`): Promise<{ auth_url: string }> {
        const response = await fetch('/api/auth/google', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ redirectUrl }),
        });

        return response.json();
    },

    /**
     * Complete Google OAuth callback
     */
    async googleCallback(code: string): Promise<AuthResponse> {
        const response = await fetch('/api/auth/google/callback', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ code }),
        });

        return response.json();
    },

    /**
     * Get current session
     */
    async getSession(): Promise<AuthResponse> {
        const response = await fetch('/api/auth/session');
        return response.json();
    },

    /**
     * Logout
     */
    async logout(): Promise<AuthResponse> {
        const response = await fetch('/api/auth/logout', {
            method: 'POST',
        });

        return response.json();
    },
};
