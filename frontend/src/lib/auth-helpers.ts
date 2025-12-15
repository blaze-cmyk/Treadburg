/**
 * Auth helper functions that ensure consistent behavior across the application
 */
import { PRODUCTION_URL } from './constants';

/**
 * Returns the correct redirect URL for OAuth providers
 * This function explicitly uses the production URL to avoid localhost redirects
 */
export function getOAuthRedirectUrl(): string {
  // Always use the production URL in OAuth flows
  return `${PRODUCTION_URL}/auth/callback`;
}

/**
 * Returns the appropriate origin for redirects
 * In development, this will be the local origin
 * In production, this will be the production URL
 */
export function getAppOrigin(): string {
  // Check if we're in a browser environment
  if (typeof window !== 'undefined') {
    // Get the browser's origin
    return window.location.origin;
  }
  
  // For server-side rendering, prioritize environment variables
  return process.env.NEXT_PUBLIC_APP_URL || 
         process.env.NEXTAUTH_URL || 
         PRODUCTION_URL;
}
