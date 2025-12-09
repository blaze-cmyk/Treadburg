import { NextRequest, NextResponse } from 'next/server'
import { supabase } from '@/lib/supabase'

// Production URL - using direct hardcoding approach for maximum reliability
const PRODUCTION_URL = 'https://tradeberg-frontend.onrender.com';

// This route handles the callback from Supabase Auth
export async function GET(request: NextRequest) {
  console.log('Auth callback triggered, processing...');
  
  const requestUrl = new URL(request.url);
  console.log('Request URL:', requestUrl.toString());
  
  const code = requestUrl.searchParams.get('code');
  console.log('Auth code present:', !!code);
  
  // Always use production URL in production
  const origin = PRODUCTION_URL;
  
  // Handle various auth parameters
  const error = requestUrl.searchParams.get('error');
  const accessToken = requestUrl.searchParams.get('access_token');
  
  if (error) {
    console.error('OAuth error returned:', error);
    return NextResponse.redirect(`${origin}/login?error=${error}`);
  }
  
  if (accessToken) {
    console.log('Access token present, redirecting to success page');
    return NextResponse.redirect(`${origin}/?auth=success&token_received=true`);
  }

  if (code) {
    try {
      console.log('Exchanging code for session...');
      // Exchange the code for a session
      const { data, error } = await supabase.auth.exchangeCodeForSession(code);

      if (error) {
        console.error('Error exchanging code for session:', error);
        return NextResponse.redirect(`${origin}/login?error=auth_callback_error&reason=${encodeURIComponent(error.message)}`);
      }

      console.log('Successfully authenticated, redirecting to home');
      // Successfully authenticated
      return NextResponse.redirect(`${origin}/?auth=success`);
    } catch (err: any) {
      console.error('Unexpected error during auth callback:', err);
      return NextResponse.redirect(`${origin}/login?error=unexpected&message=${encodeURIComponent(err?.message || 'Unknown error')}`);
    }
  }

  // No code provided
  console.log('No auth code provided, redirecting to login');
  return NextResponse.redirect(`${origin}/login?error=no_code`);
}
