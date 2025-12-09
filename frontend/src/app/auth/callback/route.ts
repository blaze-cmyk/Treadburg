import { NextRequest, NextResponse } from 'next/server'
import { createServerClient, type CookieOptions } from '@supabase/ssr'
import { cookies } from 'next/headers'

// Import constants instead of defining them here
import { PRODUCTION_URL } from '@/lib/constants'

// CRITICAL FIX: Always use the production URL for OAuth callbacks
// This prevents redirect issues across different environments
function getOrigin() {
  return PRODUCTION_URL;
}

// this route handles the callback from Supabase Auth
export async function GET(request: NextRequest) {
  const requestUrl = new URL(request.url)
  const code = requestUrl.searchParams.get('code')

  // Always use production URL for OAuth callback
  const origin = getOrigin();

  if (code) {
    const cookieStore = await cookies()

    // Create a server client that can set cookies
    const supabase = createServerClient(
      process.env.NEXT_PUBLIC_SUPABASE_URL!,
      process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
      {
        cookies: {
          get(name: string) {
            return cookieStore.get(name)?.value
          },
          set(name: string, value: string, options: CookieOptions) {
            cookieStore.set({ name, value, ...options })
          },
          remove(name: string, options: CookieOptions) {
            cookieStore.set({ name, value: '', ...options })
          },
        },
      }
    )

    try {
      // Exchange the code for a session
      const { error } = await supabase.auth.exchangeCodeForSession(code)

      if (error) {
        console.error('Error exchanging code for session:', error)
        return NextResponse.redirect(`${origin}/login?error=auth_callback_error&reason=${encodeURIComponent(error.message)}`)
      }

      // Successfully authenticated
      return NextResponse.redirect(`${origin}/?auth=success`)
    } catch (err: any) {
      console.error('Unexpected error during auth callback:', err)
      return NextResponse.redirect(`${origin}/login?error=unexpected&message=${encodeURIComponent(err?.message || 'Unknown error')}`)
    }
  }

  // No code provided
  return NextResponse.redirect(`${origin}/login?error=no_code`)
}
