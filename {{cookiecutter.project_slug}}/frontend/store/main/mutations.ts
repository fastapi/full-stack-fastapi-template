import { IUserProfile } from "@/interfaces"
import { AppNotification } from "./state"

export default {
  setToken(state, payload: string) {
    state.token = payload
  },
  setLoggedIn(state, payload: boolean) {
    state.isLoggedIn = payload
  },
  setLogInError(state, payload: boolean) {
    state.logInError = payload
  },
  setUserProfile(state, payload: IUserProfile) {
    state.userProfile = payload
  },
  setDashboardMiniDrawer(state, payload: boolean) {
    state.dashboardMiniDrawer = payload
  },
  setDashboardShowDrawer(state, payload: boolean) {
    state.dashboardShowDrawer = payload
  },
  addNotification(state, payload: AppNotification) {
    state.notifications.push(payload)
  },
  removeNotification(state, payload: AppNotification) {
    state.notifications = state.notifications.filter(
      (notification) => notification !== payload
    )
  },
}
