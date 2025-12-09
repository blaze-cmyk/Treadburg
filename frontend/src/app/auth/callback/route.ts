import { NextRequest, NextResponse } from 'next/server'
import { supabase } from '@/lib/supabase'

// This route handles the callback from Supabase Auth
export async function GET(request: NextRequest) {
  const requestUrl = new URL(request.url)
  const code = requestUrl.searchParams.get('code')

  if (code) {
    try {
      // Exchange the code for a session
      const { data, error } = await supabase.auth.exchangeCodeForSession(code)

      if (error) {
        console.error('Error exchanging code for session:', error)
        return NextResponse.redirect(`${requestUrl.origin}/login?error=auth_callback_error`)
      }

      // Successfully authenticated
      return NextResponse.redirect(`${requestUrl.origin}/?auth=success`)
    } catch (err) {
      console.error('Unexpected error during auth callback:', err)
      return NextResponse.redirect(`${requestUrl.origin}/login?error=unexpected`)
    }
  }

  // No code provided
  return NextResponse.redirect(`${requestUrl.origin}/login`)
}
