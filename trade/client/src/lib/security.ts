/**
 * Input sanitization utilities for frontend
 * Protects against XSS and injection attacks
 */

/**
 * Sanitize user input to prevent XSS attacks
 */
export function sanitizeInput(input: string): string {
    if (!input) return '';

    // Remove null bytes
    let sanitized = input.replace(/\0/g, '');

    // Escape HTML special characters
    sanitized = sanitized
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#x27;')
        .replace(/\//g, '&#x2F;');

    return sanitized;
}

/**
 * Validate email format
 */
export function validateEmail(email: string): boolean {
    const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
    return emailRegex.test(email);
}

/**
 * Validate password strength
 */
export function validatePassword(password: string): {
    isValid: boolean;
    errors: string[];
} {
    const errors: string[] = [];

    if (password.length < 12) {
        errors.push('Password must be at least 12 characters long');
    }

    if (!/[a-z]/.test(password)) {
        errors.push('Password must contain at least one lowercase letter');
    }

    if (!/[A-Z]/.test(password)) {
        errors.push('Password must contain at least one uppercase letter');
    }

    if (!/[0-9]/.test(password)) {
        errors.push('Password must contain at least one number');
    }

    if (!/[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]/.test(password)) {
        errors.push('Password must contain at least one special character');
    }

    return {
        isValid: errors.length === 0,
        errors
    };
}

/**
 * Sanitize URL to prevent javascript: and data: URLs
 */
export function sanitizeUrl(url: string): string {
    if (!url) return '';

    const trimmed = url.trim().toLowerCase();

    // Block dangerous protocols
    if (
        trimmed.startsWith('javascript:') ||
        trimmed.startsWith('data:') ||
        trimmed.startsWith('vbscript:') ||
        trimmed.startsWith('file:')
    ) {
        return '';
    }

    return url;
}

/**
 * Validate chat ID format (UUID)
 */
export function validateChatId(chatId: string): boolean {
    const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
    return uuidRegex.test(chatId);
}

/**
 * Sanitize prompt input
 */
export function sanitizePrompt(prompt: string): string {
    if (!prompt) return '';

    // Max length
    const MAX_PROMPT_LENGTH = 10000;
    let sanitized = prompt.substring(0, MAX_PROMPT_LENGTH);

    // Remove null bytes and control characters
    sanitized = sanitized.replace(/[\x00-\x1F\x7F]/g, '');

    // Trim whitespace
    sanitized = sanitized.trim();

    return sanitized;
}

/**
 * Generate CSRF token
 */
export function generateCSRFToken(): string {
    const array = new Uint8Array(32);
    crypto.getRandomValues(array);
    return Array.from(array, byte => byte.toString(16).padStart(2, '0')).join('');
}

/**
 * Store CSRF token in session storage
 */
export function storeCSRFToken(token: string): void {
    if (typeof window !== 'undefined') {
        sessionStorage.setItem('csrf_token', token);
    }
}

/**
 * Get CSRF token from session storage
 */
export function getCSRFToken(): string | null {
    if (typeof window !== 'undefined') {
        return sessionStorage.getItem('csrf_token');
    }
    return null;
}

/**
 * Validate CSRF token
 */
export function validateCSRFToken(token: string): boolean {
    const storedToken = getCSRFToken();
    return storedToken === token;
}
