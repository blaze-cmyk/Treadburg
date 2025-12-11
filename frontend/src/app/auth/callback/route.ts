import { NextRequest, NextResponse } from 'next/server'

/**
 * DEPRECATED: This route is no longer used for Google OAuth
 * 
 * The new OAuth flow uses /api/auth/google/callback which properly
 * routes through the backend API.
 * 
 * This route now redirects to the new callback to prevent conflicts.
 * 
 * If you're seeing this in production, please update your OAuth
 * redirect URLs in Supabase to:
 * https://your-domain.com/api/auth/google/callback
 */
export async function GET(request: NextRequest) {
  const requestUrl = new URL(request.url)
  const code = requestUrl.searchParams.get('code')
  const error = requestUrl.searchParams.get('error')

  // Redirect to the new callback route
  const newCallbackUrl = new URL('/api/auth/google/callback', request.url)
  
  if (code) {
    newCallbackUrl.searchParams.set('code', code)
  }
  
  if (error) {
    newCallbackUrl.searchParams.set('error', error)
  }

  console.log('⚠️ Old OAuth callback route used - redirecting to new route')
  console.log('Please update OAuth redirect URL to: /api/auth/google/callback')
  
  return NextResponse.redirect(newCallbackUrl)
}
