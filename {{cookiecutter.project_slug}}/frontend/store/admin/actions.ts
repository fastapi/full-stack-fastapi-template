import { api } from "@/api"
import { IUserProfileCreate, IUserProfileUpdate } from "@/interfaces"
// Review global namespacing https://vuex.vuejs.org/guide/modules.html

export default {
  async getUsers({ commit, dispatch, rootState }) {
    try {
      const response = await api.getUsers(rootState.main.token)
      if (response) {
        await commit("setUsers", response.data)
      }
    } catch (error) {
      await dispatch("main/checkApiError", error, { root: true })
    }
  },
  async updateUser(
    { commit, dispatch, rootState },
    payload: { id: number; user: IUserProfileUpdate }
  ) {
    try {
      const loadingNotification = {
        content: "Saving...",
        showProgress: true,
      }
      await commit("main/addNotification", loadingNotification, { root: true })
      const response = (
        await Promise.all([
          api.updateUser(rootState.main.token, payload.id, payload.user),
          // eslint-disable-next-line @typescript-eslint/no-unused-vars
          await new Promise<void>((resolve) =>
            setTimeout(() => resolve(), 500)
          ),
        ])
      )[0]
      await commit("setUser", response.data)
      await commit("main/removeNotification", loadingNotification, {
        root: true,
      })
      await commit(
        "main/addNotification",
        {
          content: "User successfully updated",
          color: "success",
        },
        { root: true }
      )
    } catch (error) {
      await dispatch("main/checkApiError", error, { root: true })
    }
  },
  async createUser(
    { commit, dispatch, rootState },
    payload: IUserProfileCreate
  ) {
    try {
      const loadingNotification = { content: "Saving...", showProgress: true }
      await commit("main/addNotification", loadingNotification, { root: true })
      const response = (
        await Promise.all([
          api.createUser(rootState.main.token, payload),
          await new Promise<void>((resolve) =>
            setTimeout(() => resolve(), 500)
          ),
        ])
      )[0]
      await commit("setUser", response.data)
      await commit("main/removeNotification", loadingNotification, {
        root: true,
      })
      await commit(
        "main/addNotification",
        {
          content: "User successfully created",
          color: "success",
        },
        { root: true }
      )
    } catch (error) {
      await dispatch("main/checkApiError", error, { root: true })
    }
  },
}
