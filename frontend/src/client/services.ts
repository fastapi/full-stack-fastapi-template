import type { CancelablePromise } from "./core/CancelablePromise"
import { OpenAPI } from "./core/OpenAPI"
import { request as __request } from "./core/request"

import type {
  Body_login_login_access_token,
  Message,
  NewPassword,
  Token,
  UserPublic,
  UpdatePassword,
  UserCreate,
  UserRegister,
  UsersPublic,
  UserUpdate,
  UserUpdateMe,
  ItemCreate,
  ItemPublic,
  ItemsPublic,
  ItemUpdate,
} from "./models"

export type TDataLoginAccessToken = {
  formData: Body_login_login_access_token
}
export type TDataRecoverPassword = {
  email: string
}
export type TDataResetPassword = {
  requestBody: NewPassword
}
export type TDataRecoverPasswordHtmlContent = {
  email: string
}

export class LoginService {
  /**
   * Login Access Token
   * OAuth2 compatible token login, get an access token for future requests
   *
   * This endpoint allows users to obtain an access token for authentication.
   * It's rate-limited to 5 requests per minute to prevent abuse.
   *
   * Args:
   * request (Request): The incoming request object (required for rate limiting).
   * response (Response): The outgoing response object (required for rate limiting).
   * session (SessionDep): The database session dependency.
   * form_data (OAuth2PasswordRequestForm): The form data containing username and password.
   *
   * Returns:
   * Token: An object containing the access token.
   *
   * Raises:
   * HTTPException:
   * - 400: If the email or password is incorrect.
   * - 400: If the user account is inactive.
   *
   * Notes:
   * This function authenticates the user, checks if the account is active,
   * and then generates and returns an access token with a specified expiration time.
   * @returns Token Successful Response
   * @throws ApiError
   */
  public static loginAccessToken(
    data: TDataLoginAccessToken,
  ): CancelablePromise<Token> {
    const { formData } = data
    return __request(OpenAPI, {
      method: "POST",
      url: "/api/v1/login/access-token",
      formData: formData,
      mediaType: "application/x-www-form-urlencoded",
      errors: {
        422: `Validation Error`,
      },
    })
  }

  /**
   * Test Token
   * Test access token
   *
   * This endpoint allows testing the validity of an access token.
   * It's protected and can only be accessed with a valid token.
   *
   * Args:
   * current_user (CurrentUser): The current authenticated user, injected by dependency.
   *
   * Returns:
   * Any: The current user's public information.
   *
   * Raises:
   * HTTPException: If the token is invalid or expired (handled by dependency).
   *
   * Notes:
   * This function is useful for verifying that a token is working correctly.
   * It simply returns the current user's information, which implicitly confirms
   * that the token is valid and the user is authenticated.
   * @returns UserPublic Successful Response
   * @throws ApiError
   */
  public static testToken(): CancelablePromise<UserPublic> {
    return __request(OpenAPI, {
      method: "POST",
      url: "/api/v1/login/test-token",
    })
  }

  /**
   * Recover Password
   * Password Recovery
   *
   * This endpoint initiates the password recovery process for a user.
   * It's rate-limited to 3 requests per minute to prevent abuse.
   *
   * Args:
   * email (str): The email address of the user requesting password recovery.
   * session (SessionDep): The database session dependency.
   * request (Request): The incoming request object (required for rate limiting).
   * response (Response): The outgoing response object (required for rate limiting).
   *
   * Returns:
   * Message: A message indicating that the password recovery email was sent.
   *
   * Raises:
   * HTTPException:
   * - 404: If no user is found with the provided email address.
   *
   * Notes:
   * This function checks for the existence of the user, generates a password reset token,
   * creates a password reset email, and sends it to the user's email address.
   * It does not confirm or deny the existence of an account to prevent email enumeration.
   * @returns Message Successful Response
   * @throws ApiError
   */
  public static recoverPassword(
    data: TDataRecoverPassword,
  ): CancelablePromise<Message> {
    const { email } = data
    return __request(OpenAPI, {
      method: "POST",
      url: "/api/v1/password-recovery/{email}",
      path: {
        email,
      },
      errors: {
        422: `Validation Error`,
      },
    })
  }

  /**
   * Reset Password
   * Reset password
   *
   * This endpoint allows users to reset their password using a valid reset token.
   * It's rate-limited to 3 requests per minute to prevent abuse.
   *
   * Args:
   * session (SessionDep): The database session dependency.
   * body (NewPassword): The new password and reset token.
   * request (Request): The incoming request object (required for rate limiting).
   * response (Response): The outgoing response object (required for rate limiting).
   *
   * Returns:
   * Message: A message indicating that the password was successfully updated.
   *
   * Raises:
   * HTTPException:
   * - 400: If the reset token is invalid.
   * - 404: If no user is found with the email associated with the token.
   * - 400: If the user account is inactive.
   *
   * Notes:
   * This function verifies the reset token, retrieves the associated user,
   * checks if the user is active, hashes the new password, and updates it in the database.
   * It's the final step in the password recovery process.
   * @returns Message Successful Response
   * @throws ApiError
   */
  public static resetPassword(
    data: TDataResetPassword,
  ): CancelablePromise<Message> {
    const { requestBody } = data
    return __request(OpenAPI, {
      method: "POST",
      url: "/api/v1/reset-password/",
      body: requestBody,
      mediaType: "application/json",
      errors: {
        422: `Validation Error`,
      },
    })
  }

  /**
   * Recover Password Html Content
   * HTML Content for Password Recovery
   *
   * This endpoint generates and returns the HTML content for a password recovery email.
   * It's protected and can only be accessed by active superusers.
   *
   * Args:
   * email (str): The email address of the user for whom to generate the recovery email.
   * session (SessionDep): The database session dependency.
   *
   * Returns:
   * HTMLResponse: The HTML content of the password reset email, with the subject in the headers.
   *
   * Raises:
   * HTTPException:
   * - 404: If no user is found with the provided email address.
   *
   * Notes:
   * This function is primarily for testing and debugging purposes. It allows superusers
   * to view the content of password reset emails without actually sending them.
   * It generates a password reset token and creates the email content just like
   * the actual password recovery process.
   * @returns string Successful Response
   * @throws ApiError
   */
  public static recoverPasswordHtmlContent(
    data: TDataRecoverPasswordHtmlContent,
  ): CancelablePromise<string> {
    const { email } = data
    return __request(OpenAPI, {
      method: "POST",
      url: "/api/v1/password-recovery-html-content/{email}",
      path: {
        email,
      },
      errors: {
        422: `Validation Error`,
      },
    })
  }
}

export type TDataReadUsers = {
  limit?: number
  skip?: number
}
export type TDataCreateUser = {
  requestBody: UserCreate
}
export type TDataUpdateUserMe = {
  requestBody: UserUpdateMe
}
export type TDataUpdatePasswordMe = {
  requestBody: UpdatePassword
}
export type TDataRegisterUser = {
  requestBody: UserRegister
}
export type TDataReadUserById = {
  userId: string
}
export type TDataUpdateUser = {
  requestBody: UserUpdate
  userId: string
}
export type TDataDeleteUser = {
  userId: string
}

export class UsersService {
  /**
   * Read Users
   * Retrieve users.
   *
   * This endpoint allows retrieving a list of users with pagination.
   * It's protected and can only be accessed by superusers.
   *
   * Args:
   * session (SessionDep): The database session dependency.
   * skip (int): The number of users to skip (for pagination).
   * limit (int): The maximum number of users to return.
   *
   * Returns:
   * UsersPublic: An object containing the list of users and the total count.
   *
   * Notes:
   * This endpoint is useful for administrative purposes to view all users in the system.
   * @returns UsersPublic Successful Response
   * @throws ApiError
   */
  public static readUsers(
    data: TDataReadUsers = {},
  ): CancelablePromise<UsersPublic> {
    const { limit = 100, skip = 0 } = data
    return __request(OpenAPI, {
      method: "GET",
      url: "/api/v1/users/",
      query: {
        skip,
        limit,
      },
      errors: {
        422: `Validation Error`,
      },
    })
  }

  /**
   * Create User
   * Create new user.
   *
   * This endpoint allows creating a new user in the system.
   * It's protected and can only be accessed by superusers.
   *
   * Args:
   * session (SessionDep): The database session dependency.
   * user_in (UserCreate): The user data to be created.
   *
   * Returns:
   * UserPublic: The created user's public information.
   *
   * Raises:
   * HTTPException:
   * - 400: If a user with the given email already exists.
   *
   * Notes:
   * If email sending is enabled, a new account email will be sent to the user.
   * @returns UserPublic Successful Response
   * @throws ApiError
   */
  public static createUser(
    data: TDataCreateUser,
  ): CancelablePromise<UserPublic> {
    const { requestBody } = data
    return __request(OpenAPI, {
      method: "POST",
      url: "/api/v1/users/",
      body: requestBody,
      mediaType: "application/json",
      errors: {
        422: `Validation Error`,
      },
    })
  }

  /**
   * Read User Me
   * Get current user.
   *
   * This endpoint allows users to retrieve their own information.
   * It's protected and can be accessed by authenticated users.
   *
   * Args:
   * current_user (CurrentUser): The current authenticated user.
   *
   * Returns:
   * UserPublic: The current user's public information.
   *
   * Notes:
   * This endpoint is useful for clients to get the latest user information after login.
   * @returns UserPublic Successful Response
   * @throws ApiError
   */
  public static readUserMe(): CancelablePromise<UserPublic> {
    return __request(OpenAPI, {
      method: "GET",
      url: "/api/v1/users/me",
    })
  }

  /**
   * Delete User Me
   * Delete own user.
   *
   * This endpoint allows users to delete their own account.
   * It's protected and can be accessed by authenticated users.
   *
   * Args:
   * session (SessionDep): The database session dependency.
   * current_user (CurrentUser): The current authenticated user.
   *
   * Returns:
   * Message: A message confirming the user deletion.
   *
   * Raises:
   * HTTPException:
   * - 403: If the user is a superuser trying to delete their own account.
   *
   * Notes:
   * Superusers are not allowed to delete their own accounts for security reasons.
   * @returns Message Successful Response
   * @throws ApiError
   */
  public static deleteUserMe(): CancelablePromise<Message> {
    return __request(OpenAPI, {
      method: "DELETE",
      url: "/api/v1/users/me",
    })
  }

  /**
   * Update User Me
   * Update own user.
   *
   * This endpoint allows users to update their own information.
   * It's protected and can be accessed by authenticated users.
   *
   * Args:
   * session (SessionDep): The database session dependency.
   * user_in (UserUpdateMe): The user data to be updated.
   * current_user (CurrentUser): The current authenticated user.
   *
   * Returns:
   * UserPublic: The updated user's public information.
   *
   * Raises:
   * HTTPException:
   * - 409: If the new email is already in use by another user.
   *
   * Notes:
   * Users can update their own information, but not their role or superuser status.
   * @returns UserPublic Successful Response
   * @throws ApiError
   */
  public static updateUserMe(
    data: TDataUpdateUserMe,
  ): CancelablePromise<UserPublic> {
    const { requestBody } = data
    return __request(OpenAPI, {
      method: "PATCH",
      url: "/api/v1/users/me",
      body: requestBody,
      mediaType: "application/json",
      errors: {
        422: `Validation Error`,
      },
    })
  }

  /**
   * Update Password Me
   * Update own password.
   *
   * This endpoint allows users to update their own password.
   * It's protected and can be accessed by authenticated users.
   *
   * Args:
   * session (SessionDep): The database session dependency.
   * body (UpdatePassword): The current and new password data.
   * current_user (CurrentUser): The current authenticated user.
   *
   * Returns:
   * Message: A message confirming the password update.
   *
   * Raises:
   * HTTPException:
   * - 400: If the current password is incorrect or if the new password is the same as the current one.
   *
   * Notes:
   * Users must provide their current password for security reasons.
   * @returns Message Successful Response
   * @throws ApiError
   */
  public static updatePasswordMe(
    data: TDataUpdatePasswordMe,
  ): CancelablePromise<Message> {
    const { requestBody } = data
    return __request(OpenAPI, {
      method: "PATCH",
      url: "/api/v1/users/me/password",
      body: requestBody,
      mediaType: "application/json",
      errors: {
        422: `Validation Error`,
      },
    })
  }

  /**
   * Register User
   * Create new user without the need to be logged in.
   *
   * This endpoint allows new users to register in the system.
   * It's public and can be accessed without authentication.
   *
   * Args:
   * session (SessionDep): The database session dependency.
   * user_in (UserRegister): The user registration data.
   *
   * Returns:
   * UserPublic: The created user's public information.
   *
   * Raises:
   * HTTPException:
   * - 400: If a user with the given email already exists.
   *
   * Notes:
   * This endpoint is typically used for user sign-up functionality.
   * @returns UserPublic Successful Response
   * @throws ApiError
   */
  public static registerUser(
    data: TDataRegisterUser,
  ): CancelablePromise<UserPublic> {
    const { requestBody } = data
    return __request(OpenAPI, {
      method: "POST",
      url: "/api/v1/users/signup",
      body: requestBody,
      mediaType: "application/json",
      errors: {
        422: `Validation Error`,
      },
    })
  }

  /**
   * Read User By Id
   * Get a specific user by id.
   *
   * This endpoint allows retrieving a specific user's information by their ID.
   * It's protected and can be accessed by the user themselves or superusers.
   *
   * Args:
   * user_id (uuid.UUID): The ID of the user to retrieve.
   * session (SessionDep): The database session dependency.
   * current_user (CurrentUser): The current authenticated user.
   *
   * Returns:
   * UserPublic: The requested user's public information.
   *
   * Raises:
   * HTTPException:
   * - 403: If the current user doesn't have enough privileges to access the information.
   * - 404: If the user with the given ID is not found.
   *
   * Notes:
   * Regular users can only access their own information, while superusers can access any user's information.
   * @returns UserPublic Successful Response
   * @throws ApiError
   */
  public static readUserById(
    data: TDataReadUserById,
  ): CancelablePromise<UserPublic> {
    const { userId } = data
    return __request(OpenAPI, {
      method: "GET",
      url: "/api/v1/users/{user_id}",
      path: {
        user_id: userId,
      },
      errors: {
        422: `Validation Error`,
      },
    })
  }

  /**
   * Update User
   * Update a user.
   *
   * This endpoint allows updating a specific user's information.
   * It's protected and can only be accessed by superusers.
   *
   * Args:
   * session (SessionDep): The database session dependency.
   * user_id (uuid.UUID): The ID of the user to update.
   * user_in (UserUpdate): The user data to be updated.
   *
   * Returns:
   * UserPublic: The updated user's public information.
   *
   * Raises:
   * HTTPException:
   * - 404: If the user with the given ID is not found.
   * - 409: If the new email is already in use by another user.
   *
   * Notes:
   * This endpoint is typically used for administrative purposes to update any user's information.
   * @returns UserPublic Successful Response
   * @throws ApiError
   */
  public static updateUser(
    data: TDataUpdateUser,
  ): CancelablePromise<UserPublic> {
    const { requestBody, userId } = data
    return __request(OpenAPI, {
      method: "PATCH",
      url: "/api/v1/users/{user_id}",
      path: {
        user_id: userId,
      },
      body: requestBody,
      mediaType: "application/json",
      errors: {
        422: `Validation Error`,
      },
    })
  }

  /**
   * Delete User
   * Delete a user.
   *
   * This endpoint allows deleting a specific user from the system.
   * It's protected and can only be accessed by superusers.
   *
   * Args:
   * session (SessionDep): The database session dependency.
   * current_user (CurrentUser): The current authenticated superuser.
   * user_id (uuid.UUID): The ID of the user to delete.
   *
   * Returns:
   * Message: A message confirming the user deletion.
   *
   * Raises:
   * HTTPException:
   * - 403: If a superuser tries to delete their own account.
   * - 404: If the user with the given ID is not found.
   *
   * Notes:
   * Superusers are not allowed to delete their own accounts for security reasons.
   * @returns Message Successful Response
   * @throws ApiError
   */
  public static deleteUser(data: TDataDeleteUser): CancelablePromise<Message> {
    const { userId } = data
    return __request(OpenAPI, {
      method: "DELETE",
      url: "/api/v1/users/{user_id}",
      path: {
        user_id: userId,
      },
      errors: {
        422: `Validation Error`,
      },
    })
  }
}

export type TDataTestEmail = {
  emailTo: string
}

export class UtilsService {
  /**
   * Test Email
   * Test emails.
   *
   * This endpoint allows sending a test email to a specified address.
   * It's protected and can only be accessed by active superusers.
   *
   * Args:
   * email_to (EmailStr): The email address to send the test email to.
   *
   * Returns:
   * Message: A message indicating that the test email was sent successfully.
   *
   * Raises:
   * HTTPException: If the user is not an active superuser.
   *
   * Notes:
   * This function is useful for verifying email functionality in the system.
   * It generates a test email and sends it to the specified address.
   * @returns Message Successful Response
   * @throws ApiError
   */
  public static testEmail(data: TDataTestEmail): CancelablePromise<Message> {
    const { emailTo } = data
    return __request(OpenAPI, {
      method: "POST",
      url: "/api/v1/utils/test-email/",
      query: {
        email_to: emailTo,
      },
      errors: {
        422: `Validation Error`,
      },
    })
  }

  /**
   * Health Check
   * Perform a health check.
   *
   * This endpoint returns True, indicating that the API is up and running.
   * It can be used for monitoring and load balancer checks.
   *
   * Args:
   * None
   *
   * Returns:
   * bool: Always returns True if the API is functioning.
   *
   * Raises:
   * None
   *
   * Notes:
   * This is an asynchronous function that doesn't require any authentication.
   * It's typically used by monitoring systems to verify the API's availability.
   * @returns boolean Successful Response
   * @throws ApiError
   */
  public static healthCheck(): CancelablePromise<boolean> {
    return __request(OpenAPI, {
      method: "GET",
      url: "/api/v1/utils/health-check/",
    })
  }
}

export type TDataReadItems = {
  limit?: number
  skip?: number
}
export type TDataCreateItem = {
  requestBody: ItemCreate
}
export type TDataReadItem = {
  id: string
}
export type TDataUpdateItem = {
  id: string
  requestBody: ItemUpdate
}
export type TDataDeleteItem = {
  id: string
}

export class ItemsService {
  /**
   * Read Items
   * Retrieve items.
   * @returns ItemsPublic Successful Response
   * @throws ApiError
   */
  public static readItems(
    data: TDataReadItems = {},
  ): CancelablePromise<ItemsPublic> {
    const { limit = 100, skip = 0 } = data
    return __request(OpenAPI, {
      method: "GET",
      url: "/api/v1/items/",
      query: {
        skip,
        limit,
      },
      errors: {
        422: `Validation Error`,
      },
    })
  }

  /**
   * Create Item
   * Create new item.
   * @returns ItemPublic Successful Response
   * @throws ApiError
   */
  public static createItem(
    data: TDataCreateItem,
  ): CancelablePromise<ItemPublic> {
    const { requestBody } = data
    return __request(OpenAPI, {
      method: "POST",
      url: "/api/v1/items/",
      body: requestBody,
      mediaType: "application/json",
      errors: {
        422: `Validation Error`,
      },
    })
  }

  /**
   * Read Item
   * Get item by ID.
   * @returns ItemPublic Successful Response
   * @throws ApiError
   */
  public static readItem(data: TDataReadItem): CancelablePromise<ItemPublic> {
    const { id } = data
    return __request(OpenAPI, {
      method: "GET",
      url: "/api/v1/items/{id}",
      path: {
        id,
      },
      errors: {
        422: `Validation Error`,
      },
    })
  }

  /**
   * Update Item
   * Update an item.
   * @returns ItemPublic Successful Response
   * @throws ApiError
   */
  public static updateItem(
    data: TDataUpdateItem,
  ): CancelablePromise<ItemPublic> {
    const { id, requestBody } = data
    return __request(OpenAPI, {
      method: "PUT",
      url: "/api/v1/items/{id}",
      path: {
        id,
      },
      body: requestBody,
      mediaType: "application/json",
      errors: {
        422: `Validation Error`,
      },
    })
  }

  /**
   * Delete Item
   * Delete an item.
   * @returns Message Successful Response
   * @throws ApiError
   */
  public static deleteItem(data: TDataDeleteItem): CancelablePromise<Message> {
    const { id } = data
    return __request(OpenAPI, {
      method: "DELETE",
      url: "/api/v1/items/{id}",
      path: {
        id,
      },
      errors: {
        422: `Validation Error`,
      },
    })
  }
}
