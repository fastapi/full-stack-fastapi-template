import type { UserPublic } from "@/client"
import { getRoleColor as getThemeRoleColor } from "../theme/colors"

export enum UserRole {
  USER = "user",
  TRAINER = "trainer",
  COUNSELOR = "counselor", 
  ADMIN = "admin",
}

/**
 * Get user role based on current user data
 */
export const getUserRole = (user: UserPublic | null): UserRole => {
  if (!user) return UserRole.USER

  // Use the role field from backend if available
  if (user.role) {
    switch (user.role.toLowerCase()) {
      case "admin":
      case "super_admin":
        return UserRole.ADMIN
      case "counselor":
        return UserRole.COUNSELOR
      case "trainer":
        return UserRole.TRAINER
      case "user":
      default:
        return UserRole.USER
    }
  }

  // Fallback to is_superuser for backwards compatibility
  if (user.is_superuser) return UserRole.ADMIN

  return UserRole.USER
}

/**
 * Check if user has permission for a specific action
 */
export const hasPermission = (
  user: UserPublic | null,
  permission: string,
): boolean => {
  const role = getUserRole(user)

  // Admin has all permissions
  if (role === UserRole.ADMIN) return true

  switch (permission) {
    // Admin-only permissions (already handled above)
    case "admin":
    case "manage_users":
    case "access_system_health":
    case "delete_souls":
      return false

    // Counselor permissions
    case "access_counselor_queue":
    case "review_responses":
    case "approve_responses":
    case "modify_responses":
    case "view_risk_assessments":
      return role === UserRole.COUNSELOR

    // Trainer permissions
    case "access_training":
    case "access_documents":
    case "access_analytics":
    case "access_rag_config":
    case "upload_documents":
    case "create_souls":
    case "edit_souls":
      return role === UserRole.TRAINER

    // Basic user permissions
    case "chat_with_souls":
      return true // All users can chat

    default:
      return false
  }
}

/**
 * Get role display name
 */
export const getRoleDisplayName = (role: UserRole): string => {
  switch (role) {
    case UserRole.ADMIN:
      return "Administrator"
    case UserRole.COUNSELOR:
      return "Counselor"
    case UserRole.TRAINER:
      return "Trainer"
    case UserRole.USER:
      return "User"
    default:
      return "User"
  }
}

/**
 * Get role color for UI display
 */
export const getRoleColor = (role: UserRole): string => {
  return getThemeRoleColor(role.toString())
}

/**
 * Check if user can access a specific route
 */
export const canAccessRoute = (
  user: UserPublic | null,
  route: string,
): boolean => {
  const role = getUserRole(user)

  // Admin can access all routes
  if (role === UserRole.ADMIN) return true

  switch (route) {
    // Admin-only routes
    case "/admin":
    case "/advanced-rag":
      return false

    // Counselor routes
    case "/counselor":
    case "/counselor-dashboard":
      return role === UserRole.COUNSELOR

    // Trainer routes
    case "/training":
    case "/documents":
    case "/training-documents":
    case "/create-soul":
      return role === UserRole.TRAINER

    // Basic user routes
    case "/ai-souls":
    case "/chat":
    case "/":
    case "/settings":
      return true // All authenticated users

    default:
      return false
  }
}
