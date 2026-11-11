/**
 * Next.js Edge Middleware – Auth guard.
 *
 * Protects all dashboard routes by checking for a valid access token cookie.
 * Runs on the Edge runtime (no Node.js APIs).
 *
 * Protected: /[orgSlug]/* (anything not in the public list below)
 * Public: /login, /register, /forgot-password, /api/*, /_next/*, /public/*
 */

import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

/** Cookie name where the access token is stored by the server on login. */
const TOKEN_COOKIE = 'systemaops_access_token'

/** Paths that do NOT require authentication. */
const PUBLIC_PATHS = [
  '/login',
  '/register',
  '/forgot-password',
  '/reset-password',
]

/** Decode a JWT payload without verifying the signature (Edge-safe). */
function decodeJWTPayload(token: string): Record<string, unknown> | null {
  try {
    const parts = token.split('.')
    if (parts.length !== 3) return null
    // Base64url decode
    const payload = parts[1].replace(/-/g, '+').replace(/_/g, '/')
    const decoded = atob(payload)
    return JSON.parse(decoded) as Record<string, unknown>
  } catch {
    return null
  }
}

/** Check whether a JWT is expired (client-side, no signature verification). */
function isTokenExpired(token: string): boolean {
  const payload = decodeJWTPayload(token)
  if (!payload || typeof payload.exp !== 'number') return true
  // Add 10-second buffer to avoid edge-case clock skew
  return Date.now() / 1000 > payload.exp - 10
}

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl

  // Always allow Next.js internals and static assets
  if (
    pathname.startsWith('/_next/') ||
    pathname.startsWith('/api/') ||
    pathname.startsWith('/public/') ||
    pathname === '/favicon.ico' ||
    pathname === '/logo.svg'
  ) {
    return NextResponse.next()
  }

  // Allow public auth paths
  if (PUBLIC_PATHS.some((p) => pathname.startsWith(p))) {
    // If already authenticated, redirect to dashboard
    const token = request.cookies.get(TOKEN_COOKIE)?.value
    if (token && !isTokenExpired(token)) {
      // Try to extract org slug from sessionStorage-like header (set by app)
      const orgSlug = request.headers.get('x-org-slug')
      if (orgSlug) {
        return NextResponse.redirect(new URL(`/${orgSlug}`, request.url))
      }
    }
    return NextResponse.next()
  }

  // Root path: redirect to login
  if (pathname === '/') {
    return NextResponse.redirect(new URL('/login', request.url))
  }

  // All other routes require authentication
  const token = request.cookies.get(TOKEN_COOKIE)?.value

  if (!token || isTokenExpired(token)) {
    const loginUrl = new URL('/login', request.url)
    loginUrl.searchParams.set('next', pathname)
    return NextResponse.redirect(loginUrl)
  }

  // Token present and not expired — attach decoded user info to headers
  // for optional use in server components (no secrets, just claims)
  const payload = decodeJWTPayload(token)
  const response = NextResponse.next()
  if (payload?.sub) {
    response.headers.set('x-user-id', String(payload.sub))
  }
  if (payload?.org_id) {
    response.headers.set('x-org-id', String(payload.org_id))
  }

  return response
}

export const config = {
  matcher: [
    /*
     * Match all paths EXCEPT:
     * - _next/static (static files)
     * - _next/image (image optimization)
     * - favicon.ico, robots.txt, sitemap.xml
     */
    '/((?!_next/static|_next/image|favicon.ico|robots.txt|sitemap.xml).*)',
  ],
}
