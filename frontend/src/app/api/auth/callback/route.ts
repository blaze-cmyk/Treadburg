import { NextRequest, NextResponse } from 'next/server'
import { cookies } from 'next/headers'

const BACKEND_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8080/api";

/**
 * This route handles email confirmation callbacks from Supabase Auth
 * (e.g., email verification, password reset confirmations)
 * 
 *
 */
export async function GET(request: NextRequest) {
  const requestUrl = new URL(request.url)
  const code = requestUrl.searchParams.get('code')
  const type = requestUrl.searchParams.get('type') // 'signup', 'recovery', etc.

  const origin = request.nextUrl.origin;

  if (code) {
    try {
      // Exchange the code for a session via backend (NOT direct Supabase access)
      const response = await fetch(`${BACKEND_URL}/auth/email/callback`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ code, type }),
      });

      const data = await response.json();

      if (!response.ok || !data.success) {
        console.error('Error exchanging code for session:', data)
        return NextResponse.redirect(`${origin}/login?error=auth_callback_error`)
      }

      // Set auth tokens in httpOnly cookies
      const redirectUrl = type === 'recovery' 
        ? `${origin}/reset-password?verified=true`
        : `${origin}/?verified=true`;
      
      const redirectResponse = NextResponse.redirect(redirectUrl);

      if (data.access_token) {
        redirectResponse.cookies.set("access_token", data.access_token, {
          httpOnly: true,
          secure: process.env.NODE_ENV === "production",
          sameSite: "lax",
          maxAge: 60 * 60 * 24 * 7, // 7 days
          path: "/",
        });

        if (data.refresh_token) {
          redirectResponse.cookies.set("refresh_token", data.refresh_token, {
            httpOnly: true,
            secure: process.env.NODE_ENV === "production",
            sameSite: "lax",
            maxAge: 60 * 60 * 24 * 30, // 30 days
            path: "/",
          });
        }
      }

      return redirectResponse;
    } catch (err) {
      console.error('Unexpected error during auth callback:', err)
      return NextResponse.redirect(`${origin}/login?error=unexpected`)
    }
  }

  // No code provided
  return NextResponse.redirect(`${origin}/login?error=no_code`)
}
