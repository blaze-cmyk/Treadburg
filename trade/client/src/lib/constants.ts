/**
 * Global application constants
 */

// Production URL - update this when your deployment URL changes
export const PRODUCTION_URL = 'https://tradeberg-frontend-qwx0.onrender.com';

// OAuth settings
export const OAUTH_REDIRECT_PATH = '/auth/callback';
export const OAUTH_SUCCESS_PATH = '/';

// Error and status messages
export const ERROR_MESSAGES = {
  AUTH_CALLBACK: 'Authentication failed. Please try again.',
  UNEXPECTED: 'An unexpected error occurred. Please try again.',
  NO_CODE: 'Authentication process was interrupted. Please try again.',
};

// Cookie names
export const COOKIES = {
  REDIRECT_AFTER_LOGIN: 'redirect_after_login',
};
