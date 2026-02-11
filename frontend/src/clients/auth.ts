const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:80"
const API_PREFIX: string = "/api/v1"

export interface SignupRequest {
  email: string
  password: string
}

export interface LoginRequest {
  email: string
  password: string
}

export interface UserResponse {
  user_id: number
  email: string
  user_name: string
  is_active: boolean
  is_verified: boolean
  created_at: string
  profile_complete: boolean
  full_name?: string // alias for user_name for backward compatibility
}

export interface TokenResponse {
  access_token: string
  refresh_token: string
  token_type: string
  user: UserResponse
}

export interface ApiError {
  detail: string
}

class AuthAPI {
  private readonly baseUrl: string
  private readonly apiPrefix: string

  constructor(baseUrl: string = API_BASE_URL, apiPrefix: string = API_PREFIX) {
    this.baseUrl = baseUrl
    this.apiPrefix = apiPrefix
  }

  async signup(data: SignupRequest): Promise<TokenResponse> {
    const response = await fetch(
      `${this.baseUrl}${this.apiPrefix}/auth/signup`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(data),
      },
    )

    if (!response.ok) {
      const error: ApiError = await response.json()
      throw new Error(error.detail || "Signup failed")
    }

    return response.json()
  }

  async login(data: LoginRequest): Promise<TokenResponse> {
    const response = await fetch(
      `${this.baseUrl}${this.apiPrefix}/auth/login`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(data),
      },
    )

    if (!response.ok) {
      const error: ApiError = await response.json()
      throw new Error(error.detail || "Login failed")
    }

    return response.json()
  }
}

export const authAPI = new AuthAPI()
