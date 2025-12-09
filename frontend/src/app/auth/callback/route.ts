import { NextRequest, NextResponse } from 'next/server'
import { supabase } from '@/lib/supabase'

// Helper to get the actual origin (handles proxy/Render case)
function getOrigin(request: NextRequest) {
  if (process.env.NEXT_PUBLIC_APP_URL) {
    return process.env.NEXT_PUBLIC_APP_URL;
  }
  const forwardedHost = request.headers.get('x-forwarded-host');
  if (forwardedHost) {
    return `https://${forwardedHost}`;
  }
  return request.nextUrl.origin;
}

// This route handles the callback from Supabase Auth
export async function GET(request: NextRequest) {
  const requestUrl = new URL(request.url)
  const code = requestUrl.searchParams.get('code')
  const origin = getOrigin(request)

  if (code) {
    try {
      // Exchange the code for a session
      const { data, error } = await supabase.auth.exchangeCodeForSession(code)

      if (error) {
        console.error('Error exchanging code for session:', error)
        return NextResponse.redirect(`${origin}/login?error=auth_callback_error`)
      }

      // Successfully authenticated
      return NextResponse.redirect(`${origin}/?auth=success`)
    } catch (err) {
      console.error('Unexpected error during auth callback:', err)
      return NextResponse.redirect(`${origin}/login?error=unexpected`)
    }
  }

  // No code provided
  return NextResponse.redirect(`${origin}/login`)
}
