import { NextRequest, NextResponse } from 'next/server'
import { cookies } from 'next/headers'
import { supabase } from '@/lib/supabase'

// This route handles the callback from Supabase Auth email confirmations
export async function GET(request: NextRequest) {
  const requestUrl = new URL(request.url)
  const code = requestUrl.searchParams.get('code')
  
  if (code) {
    try {
      // Exchange the code for a session
      const { data, error } = await supabase.auth.exchangeCodeForSession(code)
      
      if (error) {
        console.error('Error exchanging code for session:', error)
        return NextResponse.redirect(new URL('/login?error=auth_callback_error', request.url))
      }
      
      // Successfully authenticated
      return NextResponse.redirect(new URL('/?auth=success', request.url))
    } catch (err) {
      console.error('Unexpected error during auth callback:', err)
      return NextResponse.redirect(new URL('/login?error=unexpected', request.url))
    }
  }

  // No code provided
  return NextResponse.redirect(new URL('/login', request.url))
}
