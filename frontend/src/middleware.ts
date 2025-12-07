import { createMiddlewareClient } from '@supabase/auth-helpers-nextjs'
import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

// This middleware protects authenticated routes and redirects unauthenticated users
export async function middleware(req: NextRequest) {
  // Create a Supabase client configured to use cookies
  const res = NextResponse.next()
  const supabase = createMiddlewareClient({ req, res })
  
  // Refresh session if expired - required for Server Components
  const { data: { session } } = await supabase.auth.getSession()

  // Public paths that don't require authentication
  const publicPaths = ['/login', '/reset-password', '/auth/callback']
  const isPublicPath = publicPaths.some(path => 
    req.nextUrl.pathname === path || req.nextUrl.pathname.startsWith(`${path}/`)
  )

  // Check authentication status for protected routes
  if (!session && !isPublicPath) {
    // Redirect unauthenticated users to login page
    const redirectUrl = new URL('/login', req.url)
    
    // Add the requested URL as a query param to enable redirection after login
    redirectUrl.searchParams.set('redirectTo', req.nextUrl.pathname)
    
    return NextResponse.redirect(redirectUrl)
  }

  // If user is authenticated and trying to access login page, redirect to home
  if (session && isPublicPath && !req.nextUrl.pathname.startsWith('/auth/callback')) {
    return NextResponse.redirect(new URL('/', req.url))
  }

  return res
}

// Define which paths this middleware should run on
export const config = {
  // Match all routes except for static files, api routes, and _next
  matcher: ['/((?!_next/static|_next/image|favicon.ico|images/|api/).*)'],
}
