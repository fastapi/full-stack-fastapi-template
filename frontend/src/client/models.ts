export type Body_login_login_access_token = {
  grant_type?: string | null
  username: string
  password: string
  scope?: string
  client_id?: string | null
  client_secret?: string | null
}

export type HTTPValidationError = {
  detail?: Array<ValidationError>
}

export type ItemCreate = {
  title: string
  description?: string | null
}

export type ItemPublic = {
  title: string
  description?: string | null
  id: string
  owner_id: string
}

export type ItemUpdate = {
  title?: string | null
  description?: string | null
}

export type ItemsPublic = {
  data: Array<ItemPublic>
  count: number
}

/**
 * Generic message.
 *
 * Defines a simple structure for generic messages.
 *
 * Args:
 * message (str): The content of the message.
 *
 * Returns:
 * None
 *
 * Notes:
 * This class can be used for various messaging purposes throughout the application.
 */
export type Message = {
  message: string
}

/**
 * Class for resetting password.
 *
 * Defines the structure for a password reset request.
 *
 * Args:
 * token (str): The token for password reset verification.
 * new_password (str): The new password to set, with length constraints.
 *
 * Returns:
 * None
 *
 * Notes:
 * This class is used in the password reset process.
 */
export type NewPassword = {
  token: string
  new_password: string
}

/**
 * JSON payload containing access token.
 *
 * Defines the structure for an authentication token response.
 *
 * Args:
 * access_token (str): The access token string.
 * token_type (str): The type of token, defaults to "bearer".
 *
 * Returns:
 * None
 *
 * Notes:
 * This class is used in the authentication process to return token information.
 */
export type Token = {
  access_token: string
  token_type?: string
}

/**
 * Class for updating user password.
 */
export type UpdatePassword = {
  current_password: string
  new_password: string
}

/**
 * Class for creating a new user.
 */
export type UserCreate = {
  email: string
  is_active?: boolean
  is_superuser?: boolean
  full_name?: string | null
  password: string
}

/**
 * Public properties for user.
 */
export type UserPublic = {
  email: string
  is_active?: boolean
  is_superuser?: boolean
  full_name?: string | null
  id: string
}

/**
 * Class for user registration.
 */
export type UserRegister = {
  email: string
  password: string
  full_name?: string | null
}

/**
 * Class for updating user information.
 */
export type UserUpdate = {
  email?: string | null
  is_active?: boolean
  is_superuser?: boolean
  full_name?: string | null
  password?: string | null
}

/**
 * Class for updating user information.
 */
export type UserUpdateMe = {
  full_name?: string | null
  email?: string | null
}

/**
 * Public properties for users.
 */
export type UsersPublic = {
  data: Array<UserPublic>
  count: number
}

export type ValidationError = {
  loc: Array<string | number>
  msg: string
  type: string
}
