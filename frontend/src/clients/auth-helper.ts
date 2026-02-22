/**
 * Shared auth token helper that bridges Clerk's React-based getToken()
 * to the non-React API client classes.
 *
 * Usage:
 * 1. In a React component inside ClerkProvider, call setGetTokenFn(getToken)
 * 2. In API clients, call getAuthToken() to get the current Bearer token
 */

let getTokenFn: (() => Promise<string | null>) | null = null

export function setGetTokenFn(fn: () => Promise<string | null>) {
  getTokenFn = fn
}

export async function getAuthToken(): Promise<string | null> {
  if (getTokenFn) return getTokenFn()
  return null
}
