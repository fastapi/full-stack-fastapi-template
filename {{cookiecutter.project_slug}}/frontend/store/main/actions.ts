import { api } from "@/api"
import { getLocalToken, removeLocalToken, saveLocalToken } from "@/utils"
import { AxiosError } from "axios"
import { IUserOpenProfileCreate } from "@/interfaces"
import { AppNotification } from "./state"

export default {
  async logIn(
    { commit, dispatch },
    payload: { username: string; password: string }
  ) {
    try {
      const response = await api.logInGetToken(
        payload.username,
        payload.password
      )
      const token = response.data.access_token
      if (token) {
        saveLocalToken(token)
        await commit("setToken", token)
        await commit("setLoggedIn", true)
        await commit("setLogInError", false)
        await dispatch("getUserProfile")
      } else {
        await dispatch("logOut")
      }
    } catch (error) {
      commit("setLogInError", true)
      await dispatch("logOut")
    }
  },
  async getUserProfile({ commit, dispatch, state }) {
    try {
      const response = await api.getMe(state.token)
      if (response.data) {
        await commit("setUserProfile", response.data)
      }
    } catch (error) {
      await dispatch("checkApiError", error)
    }
  },
  async updateUserProfile({ commit, dispatch, state }, payload) {
    try {
      const loadingNotification = { content: "Saving...", showProgress: true }
      await commit("addNotification", loadingNotification)
      const response = (
        await Promise.all([
          api.updateMe(state.token, payload),
          await new Promise<void>((resolve) =>
            setTimeout(() => resolve(), 500)
          ),
        ])
      )[0]
      await commit("setUserProfile", response.data)
      await commit("removeNotification", loadingNotification)
      await commit("addNotification", {
        content: "Profile successfully updated",
        color: "success",
      })
    } catch (error) {
      await dispatch("checkApiError", error)
    }
  },
  async createUserProfile(
    { commit, dispatch },
    payload: IUserOpenProfileCreate
  ) {
    try {
      const loadingNotification = { content: "Creating...", showProgress: true }
      await commit("addNotification", loadingNotification)
      await Promise.all([
        api.createMe(payload),
        await new Promise<void>((resolve) => setTimeout(() => resolve(), 500)),
      ])
      await commit("removeNotification", loadingNotification)
      await commit("addNotification", {
        content: "Account successfully created",
        color: "success",
      })
    } catch (error) {
      // console.log(error.response)
      await dispatch("checkApiError", error)
    }
  },
  async checkLoggedIn({ commit, dispatch, state }) {
    if (!state.isLoggedIn) {
      let token = state.token
      if (!token) {
        const localToken = getLocalToken()
        if (localToken) {
          await commit("setToken", token)
          token = localToken
        }
      }
      if (token) {
        try {
          const response = await api.getMe(token)
          await commit("setLoggedIn", true)
          await commit("setUserProfile", response.data)
        } catch (error) {
          await dispatch("logOut")
        }
      } else {
        await dispatch("logOut")
      }
    }
  },
  async logOut({ commit }) {
    removeLocalToken()
    await commit("setToken", "")
    await commit("setLoggedIn", false)
    await commit("setUserProfile", null)
  },
  async checkApiError({ dispatch }, payload: AxiosError) {
    // console.log(payload.response)
    if (payload.response!.status === 401) {
      await dispatch("logOut")
    }
  },
  async removeNotification(
    { commit },
    payload: { notification: AppNotification; timeout: number }
  ) {
    return await new Promise((resolve) => {
      setTimeout(() => {
        commit("removeNotification", payload.notification)
        resolve(true)
      }, payload.timeout)
    })
  },
  async passwordRecovery({ commit, dispatch }, payload: { username: string }) {
    try {
      await Promise.all([
        api.passwordRecovery(payload.username),
        await new Promise<void>((resolve) => setTimeout(() => resolve(), 500)),
      ])
    } catch (error) {}
    // Refactored this ... shouldn't give user indication if their attempt was successful or not
    await dispatch("logOut")
    const loadingNotification = {
      content: "Sending password recovery email",
      showProgress: true,
    }
    await commit("addNotification", loadingNotification)
  },
  async resetPassword(
    { commit, dispatch },
    payload: { password: string; token: string }
  ) {
    const loadingNotification = {
      content: "Resetting password",
      showProgress: true,
    }
    try {
      await commit("addNotification", loadingNotification)
      await Promise.all([
        api.resetPassword(payload.password, payload.token),
        await new Promise<void>((resolve) => setTimeout(() => resolve(), 500)),
      ])
      await commit("removeNotification", loadingNotification)
      await commit("addNotification", {
        content: "Password successfully reset",
        color: "success",
      })
      await dispatch("logOut")
    } catch (error) {
      await commit("removeNotification", loadingNotification)
      await commit("addNotification", {
        color: "error",
        content: "Error resetting password",
      })
    }
  },
}
