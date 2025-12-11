import { NextRequest, NextResponse } from 'next/server'
import { cookies } from 'next/headers'
import { supabase } from '@/lib/supabase'

/**
 * This route handles email confirmation callbacks from Supabase Auth
 * (e.g., email verification, password reset confirmations)
 * 
 * Note: This is different from Google OAuth which uses /api/auth/google/callback
 */
export async function GET(request: NextRequest) {
  const requestUrl = new URL(request.url)
  const code = requestUrl.searchParams.get('code')
  const type = requestUrl.searchParams.get('type') // 'signup', 'recovery', etc.

  const origin = request.nextUrl.origin;

  if (code) {
    try {
      // Exchange the code for a session
      const { data, error } = await supabase.auth.exchangeCodeForSession(code)

      if (error) {
        console.error('Error exchanging code for session:', error)
        return NextResponse.redirect(`${origin}/login?error=auth_callback_error`)
      }

      // Successfully authenticated - redirect based on type
      if (type === 'recovery') {
        // Password reset - redirect to reset password page
        return NextResponse.redirect(`${origin}/reset-password?verified=true`)
      }

      // Email verification or other - redirect to home page (which creates a new chat)
      return NextResponse.redirect(`${origin}/?verified=true`)
    } catch (err) {
      console.error('Unexpected error during auth callback:', err)
      return NextResponse.redirect(`${origin}/login?error=unexpected`)
    }
  }

  // No code provided
  return NextResponse.redirect(`${origin}/login?error=no_code`)
}
