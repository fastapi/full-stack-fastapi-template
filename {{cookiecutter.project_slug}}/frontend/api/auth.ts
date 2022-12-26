import {
    IUserProfile,
    IUserProfileUpdate,
    IUserProfileCreate,
    IUserOpenProfileCreate,
    ITokenResponse,
    ISendEmail,
    IMsg
  } from "@/interfaces"
import { apiCore } from "./core"

export const apiAuth = {
  // TEST
  async getTestText() {
    return await useFetch<IMsg>(`${apiCore.url()}/users/tester`)
  },
  // MEMBER AUTH N AUTH
  async logInGetToken(username: string, password: string) {
    // Version of this: https://github.com/unjs/ofetch/issues/37#issuecomment-1262226065
    // useFetch is borked, so you'll need to ignore errors https://github.com/unjs/ofetch/issues/37
    const params = new URLSearchParams()
    params.append("username", username)
    params.append("password", password)
    return await useFetch<ITokenResponse>(`${apiCore.url()}/login/access-token`,
      {
        method: "POST",
        body: params,
        // @ts-ignore
        headers: { "Content-Disposition": params }
      }
    )
  },
  async getRefreshedToken(token: string) {
    return await useFetch<ITokenResponse>(`${apiCore.url()}/login/refresh-token`,
      {
        method: "POST",
        headers: apiCore.headers(token)
      }
    )
  },
  async revokeRefreshedToken(token: string) {
    return await useFetch<IMsg>(`${apiCore.url()}/login/revoke-token`,
      {
        method: "POST",
        headers: apiCore.headers(token)
      }
    )
  },
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
  async recoverPassword(email: string) {
    return await useFetch<IMsg>(`${apiCore.url()}/password-recovery/${email}`,
      {
        method: "POST",
      }
    )
  },
  async resetPassword(password: string, token: string) {
    return await useFetch<IMsg>(`${apiCore.url()}/reset-password`,
      {
        method: "POST",
        body: {
          new_password: password,
          token,
          }
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