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

export const itemsCreateItem = <ThrowOnError extends boolean = false>(
  options: Parameters<typeof sdk.itemsCreateItem<ThrowOnError>>[0]
) => {
  return sdk.itemsCreateItem({ ...options, client: apiClient })
}

export const itemsUpdateItem = <ThrowOnError extends boolean = false>(
  options: Parameters<typeof sdk.itemsUpdateItem<ThrowOnError>>[0]
) => {
  return sdk.itemsUpdateItem({ ...options, client: apiClient })
}

export const itemsDeleteItem = <ThrowOnError extends boolean = false>(
  options: Parameters<typeof sdk.itemsDeleteItem<ThrowOnError>>[0]
) => {
  return sdk.itemsDeleteItem({ ...options, client: apiClient })
}

export const itemsReadItem = <ThrowOnError extends boolean = false>(
  options: Parameters<typeof sdk.itemsReadItem<ThrowOnError>>[0]
) => {
  return sdk.itemsReadItem({ ...options, client: apiClient })
}

// User management API functions
export const usersCreateUser = <ThrowOnError extends boolean = false>(
  options: Parameters<typeof sdk.usersCreateUser<ThrowOnError>>[0]
) => {
  return sdk.usersCreateUser({ ...options, client: apiClient })
}

export const usersUpdateUser = <ThrowOnError extends boolean = false>(
  options: Parameters<typeof sdk.usersUpdateUser<ThrowOnError>>[0]
) => {
  return sdk.usersUpdateUser({ ...options, client: apiClient })
}

export const usersDeleteUser = <ThrowOnError extends boolean = false>(
  options: Parameters<typeof sdk.usersDeleteUser<ThrowOnError>>[0]
) => {
  return sdk.usersDeleteUser({ ...options, client: apiClient })
}

export const usersReadUserById = <ThrowOnError extends boolean = false>(
  options: Parameters<typeof sdk.usersReadUserById<ThrowOnError>>[0]
) => {
  return sdk.usersReadUserById({ ...options, client: apiClient })
}

export const usersUpdateUserMe = <ThrowOnError extends boolean = false>(
  options: Parameters<typeof sdk.usersUpdateUserMe<ThrowOnError>>[0]
) => {
  return sdk.usersUpdateUserMe({ ...options, client: apiClient })
}

export const usersUpdatePasswordMe = <ThrowOnError extends boolean = false>(
  options: Parameters<typeof sdk.usersUpdatePasswordMe<ThrowOnError>>[0]
) => {
  return sdk.usersUpdatePasswordMe({ ...options, client: apiClient })
}

export const usersDeleteUserMe = <ThrowOnError extends boolean = false>(
  options?: Parameters<typeof sdk.usersDeleteUserMe<ThrowOnError>>[0]
) => {
  return sdk.usersDeleteUserMe({ ...options, client: apiClient })
}

export const utilsHealthCheck = <ThrowOnError extends boolean = false>(
  options?: Parameters<typeof sdk.utilsHealthCheck<ThrowOnError>>[0]
) => {
  return sdk.utilsHealthCheck({ ...options, client: apiClient })
}

// Re-export types
export * from '@/client/types.gen'
