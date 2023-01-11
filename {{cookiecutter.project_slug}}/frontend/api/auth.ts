import {
    IUserProfile,
    IUserProfileUpdate,
    IUserProfileCreate,
    IUserOpenProfileCreate,
    ITokenResponse,
    IWebToken,
    INewTOTP,
    IEnableTOTP,
    IMsg
  } from "@/interfaces"
import { apiCore } from "./core"

export const apiAuth = {
  // TEST
  async getTestText() {
    return await useFetch<IMsg>(`${apiCore.url()}/users/tester`)
  },
  // LOGIN WITH MAGIC LINK OR OAUTH2 (USERNAME/PASSWORD)
  async loginWithMagicLink(email: string) {
    return await useFetch<IWebToken>(`${apiCore.url()}/login/magic/${email}`,
      {
        method: "POST",
      }
    )
  },
  async validateMagicLink(token: string, data: IWebToken) {
    return await useFetch<ITokenResponse>(`${apiCore.url()}/login/claim`,
      {
        method: "POST",
        body: data,
        headers: apiCore.headers(token)
      }
    )
  },
  async loginWithOauth(username: string, password: string) {
    // Version of this: https://github.com/unjs/ofetch/issues/37#issuecomment-1262226065
    // useFetch is borked, so you'll need to ignore errors https://github.com/unjs/ofetch/issues/37
    const params = new URLSearchParams()
    params.append("username", username)
    params.append("password", password)
    return await useFetch<ITokenResponse>(`${apiCore.url()}/login/oauth`,
      {
        method: "POST",
        body: params,
        // @ts-ignore
        headers: { "Content-Disposition": params }
      }
    )
  },
  // TOTP SETUP AND AUTHENTICATION
  async loginWithTOTP(token: string, data: IWebToken) {
    return await useFetch<ITokenResponse>(`${apiCore.url()}/login/totp`,
      {
        method: "POST",
        body: data,
        headers: apiCore.headers(token)
      }
    )
  },
  async requestNewTOTP(token: string) {
    return await useFetch<INewTOTP>(`${apiCore.url()}/users/new-totp`,
      {
        method: "POST",
        headers: apiCore.headers(token)
      }
    )
  },
  async enableTOTPAuthentication(token: string, data: IEnableTOTP) {
    return await useFetch<IMsg>(`${apiCore.url()}/login/totp`,
      {
        method: "PUT",
        body: data,
        headers: apiCore.headers(token)
      }
    )
  },
  async disableTOTPAuthentication(token: string, data: IUserProfileUpdate) {
    return await useFetch<IMsg>(`${apiCore.url()}/login/totp`, 
      {
        method: "DELETE",
        body: data,
        headers: apiCore.headers(token)
      }
    )
  },
  // MANAGE JWT TOKENS (REFRESH / REVOKE)
  async getRefreshedToken(token: string) {
    return await useFetch<ITokenResponse>(`${apiCore.url()}/login/refresh`,
      {
        method: "POST",
        headers: apiCore.headers(token)
      }
    )
  },
  async revokeRefreshedToken(token: string) {
    return await useFetch<IMsg>(`${apiCore.url()}/login/revoke`,
      {
        method: "POST",
        headers: apiCore.headers(token)
      }
    )
  },
  // USER PROFILE MANAGEMENT
  async createProfile(data: IUserOpenProfileCreate) {
    return await useFetch<IUserProfile>(`${apiCore.url()}/users/`, 
      {
        method: "POST",
        body: data,
      }
    )
  },
  async getProfile(token: string) {
    return await useFetch<IUserProfile>(`${apiCore.url()}/users/`,
      {
        headers: apiCore.headers(token)
      }
    )
  },
  async updateProfile(token: string, data: IUserProfileUpdate) {
    return await useFetch<IUserProfile>(`${apiCore.url()}/users/`, 
      {
        method: "PUT",
        body: data,
        headers: apiCore.headers(token)
      }
    )
  },
  // ACCOUNT RECOVERY
  async recoverPassword(email: string) {
    return await useFetch<IMsg | IWebToken>(`${apiCore.url()}/login/recover/${email}`,
      {
        method: "POST",
      }
    )
  },
  async resetPassword(password: string, claim: string, token: string) {
    return await useFetch<IMsg>(`${apiCore.url()}/login/reset`,
      {
        method: "POST",
        body: {
          new_password: password,
          claim,
        },
        headers: apiCore.headers(token)
      }
    )
  },
  async requestValidationEmail(token: string) {
    return await useFetch<IMsg>(`${apiCore.url()}/users/send-validation-email`,
      {
        method: "POST",
        headers: apiCore.headers(token)
      }
    )
  },
  async validateEmail(token: string, validation: string) {
    return await useFetch<IMsg>(`${apiCore.url()}/users/validate-email`,
      {
        method: "POST",
        body: { validation },
        headers: apiCore.headers(token)
      }
    )
  },
  // ADMIN USER MANAGEMENT
  async getAllUsers(token: string) {
    return await useFetch<IUserProfile[]>(`${apiCore.url()}/users/all`,
      {
        headers: apiCore.headers(token)
      }
    )
  },
  async toggleUserState(token: string, data: IUserProfileUpdate) {
    return await useFetch<IMsg>(`${apiCore.url()}/users/toggle-state`, 
      {
        method: "POST",
        body: data,
        headers: apiCore.headers(token)
      }
    )
  },
  async createUserProfile(token: string, data: IUserProfileCreate) {
    return await useFetch<IUserProfile>(`${apiCore.url()}/users/create`, 
      {
        method: "POST",
        body: data,
        headers: apiCore.headers(token)
      }
    )
  },
}