import { createClient, createConfig } from '@/client/client'
import type { ClientOptions } from '@/client/types.gen'
import * as sdk from '@/client/sdk.gen'

// Create a configured client instance that points to the FastAPI backend
const apiClient = createClient(createConfig<ClientOptions>({
  baseUrl: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
}))

// Export configured API functions
export const loginLoginAccessToken = <ThrowOnError extends boolean = false>(
  options: Parameters<typeof sdk.loginLoginAccessToken<ThrowOnError>>[0]
) => {
  return sdk.loginLoginAccessToken({ ...options, client: apiClient })
}

// Re-export types
export * from '@/client/types.gen'
