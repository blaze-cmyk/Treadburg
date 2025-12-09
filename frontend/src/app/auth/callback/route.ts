import { NextRequest, NextResponse } from 'next/server'
import { createServerClient, type CookieOptions } from '@supabase/ssr'
import { cookies } from 'next/headers'

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

// this route handles the callback from Supabase Auth
export async function GET(request: NextRequest) {
  const requestUrl = new URL(request.url)
  const code = requestUrl.searchParams.get('code')

  // Use dynamic origin but fallback to production URL if needed
  const origin = getOrigin(request);

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
