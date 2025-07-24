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

export const usersReadUsers = <ThrowOnError extends boolean = false>(
  options?: Parameters<typeof sdk.usersReadUsers<ThrowOnError>>[0]
) => {
  return sdk.usersReadUsers({ ...options, client: apiClient })
}

export const usersReadUserMe = <ThrowOnError extends boolean = false>(
  options?: Parameters<typeof sdk.usersReadUserMe<ThrowOnError>>[0]
) => {
  return sdk.usersReadUserMe({ ...options, client: apiClient })
}

export const itemsReadItems = <ThrowOnError extends boolean = false>(
  options?: Parameters<typeof sdk.itemsReadItems<ThrowOnError>>[0]
) => {
  return sdk.itemsReadItems({ ...options, client: apiClient })
}

export const utilsHealthCheck = <ThrowOnError extends boolean = false>(
  options?: Parameters<typeof sdk.utilsHealthCheck<ThrowOnError>>[0]
) => {
  return sdk.utilsHealthCheck({ ...options, client: apiClient })
}

// ColPali API functions
export const colpaliSearchDocuments = <ThrowOnError extends boolean = false>(
  options: Parameters<typeof sdk.colpaliSearchDocuments<ThrowOnError>>[0]
) => {
  return sdk.colpaliSearchDocuments({ ...options, client: apiClient })
}

export const colpaliUploadDataset = <ThrowOnError extends boolean = false>(
  options: Parameters<typeof sdk.colpaliUploadDataset<ThrowOnError>>[0]
) => {
  return sdk.colpaliUploadDataset({ ...options, client: apiClient })
}

export const colpaliListCollections = <ThrowOnError extends boolean = false>(
  options?: Parameters<typeof sdk.colpaliListCollections<ThrowOnError>>[0]
) => {
  return sdk.colpaliListCollections({ ...options, client: apiClient })
}

export const colpaliGetCollectionInfo = <ThrowOnError extends boolean = false>(
  options: Parameters<typeof sdk.colpaliGetCollectionInfo<ThrowOnError>>[0]
) => {
  return sdk.colpaliGetCollectionInfo({ ...options, client: apiClient })
}

export const colpaliDeleteCollection = <ThrowOnError extends boolean = false>(
  options: Parameters<typeof sdk.colpaliDeleteCollection<ThrowOnError>>[0]
) => {
  return sdk.colpaliDeleteCollection({ ...options, client: apiClient })
}

export const colpaliCreateCollection = <ThrowOnError extends boolean = false>(
  options: Parameters<typeof sdk.colpaliCreateCollection<ThrowOnError>>[0]
) => {
  return sdk.colpaliCreateCollection({ ...options, client: apiClient })
}

export const colpaliHealthCheck = <ThrowOnError extends boolean = false>(
  options?: Parameters<typeof sdk.colpaliHealthCheck<ThrowOnError>>[0]
) => {
  return sdk.colpaliHealthCheck({ ...options, client: apiClient })
}

// Re-export types
export * from '@/client/types.gen'
