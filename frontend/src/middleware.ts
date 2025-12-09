import { createServerClient, type CookieOptions } from '@supabase/ssr'
import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

// This middleware protects authenticated routes and redirects unauthenticated users
export async function middleware(req: NextRequest) {
  let response = NextResponse.next({
    request: {
      headers: req.headers,
    },
  })

  const supabase = createServerClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
    {
      cookies: {
        get(name: string) {
          return req.cookies.get(name)?.value
        },
        set(name: string, value: string, options: CookieOptions) {
          response.cookies.set({
            name,
            value,
            ...options,
          })
        },
        remove(name: string, options: CookieOptions) {
          response.cookies.set({
            name,
            value: '',
            ...options,
          })
        },
      },
    }
  )

  // Refresh session if expired - required for Server Components
  const { data: { session } } = await supabase.auth.getSession()

  // Public paths that don't require authentication
  const publicPaths = ['/login', '/reset-password', '/auth/callback']
  const isPublicPath = publicPaths.some(path =>
    req.nextUrl.pathname === path || req.nextUrl.pathname.startsWith(`${path}/`)
  )

  // Helper to get the actual origin
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

  // Check authentication status for protected routes
  if (!session && !isPublicPath) {
    // Redirect unauthenticated users to login page
    const origin = getOrigin(req);
    const redirectUrl = new URL('/login', origin)

    // Add the requested URL as a query param to enable redirection after login
    redirectUrl.searchParams.set('redirectTo', req.nextUrl.pathname)

    return NextResponse.redirect(redirectUrl)
  }

  // If user is authenticated and trying to access login page, redirect to home
  if (session && isPublicPath && !req.nextUrl.pathname.startsWith('/auth/callback')) {
    const origin = getOrigin(req);
    return NextResponse.redirect(new URL('/', origin))
  }

  return response
}

// Define which paths this middleware should run on
export const config = {
  // Match all routes except for static files, api routes, and _next
  matcher: ['/((?!_next/static|_next/image|favicon.ico|images/|api/).*)'],
}
