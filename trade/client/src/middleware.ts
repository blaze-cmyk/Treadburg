import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

// This middleware protects authenticated routes and redirects unauthenticated users
export async function middleware(req: NextRequest) {
  // Redirect old deployment URL to new deployment URL
  const host = req.headers.get('host') || '';
  if (host === 'tradeberg-frontend.onrender.com') {
    const newUrl = new URL(req.url);
    newUrl.host = 'tradeberg-frontend-qwx0.onrender.com';
    return NextResponse.redirect(newUrl, 301); // Permanent redirect
  }

  let response = NextResponse.next({
    request: {
      headers: req.headers,
    },
  })

  // Check for backend auth cookies (access_token set by backend)
  const accessToken = req.cookies.get('access_token')?.value
  const isAuthenticated = !!accessToken

  // Public paths that don't require authentication
  const publicPaths = ['/login', '/reset-password', '/api/auth/google/callback']
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
  if (!isAuthenticated && !isPublicPath) {
    // Redirect unauthenticated users to login page
    const origin = getOrigin(req);
    const redirectUrl = new URL('/login', origin)

    // Store the requested URL in a cookie instead of a query param
    // This avoids issues with the redirect URL being visible in the browser
    response.cookies.set({
      name: 'redirect_after_login',
      value: req.nextUrl.pathname,
      maxAge: 60 * 10, // 10 minutes
      path: '/',
    })

    return NextResponse.redirect(redirectUrl)
  }

  // If user is authenticated and trying to access login page, redirect to home
  // But allow callback routes to complete
  if (isAuthenticated && isPublicPath && !req.nextUrl.pathname.startsWith('/api/auth/google/callback')) {
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
