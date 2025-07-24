/**
 * Authentication utility functions
 */

/**
 * Check if user is authenticated by verifying access token exists
 * @returns boolean indicating if user is authenticated
 */
export function isAuthenticated(): boolean {
  if (typeof window === 'undefined') {
    // Server-side rendering - assume not authenticated
    return false
  }
  
  const accessToken = localStorage.getItem('access_token')
  return !!accessToken
}

/**
 * Get the access token from localStorage
 * @returns string | null - the access token or null if not found
 */
export function getAccessToken(): string | null {
  if (typeof window === 'undefined') {
    return null
  }
  
  return localStorage.getItem('access_token')
}

/**
 * Clear authentication tokens from localStorage
 */
export function clearAuthTokens(): void {
  if (typeof window === 'undefined') {
    return
  }
  
  localStorage.removeItem('access_token')
  localStorage.removeItem('refresh_token')
}
