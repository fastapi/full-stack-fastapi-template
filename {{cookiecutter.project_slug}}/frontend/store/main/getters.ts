export default {
  hasAdminAccess: (state) => {
    return (
      state.userProfile &&
      state.userProfile.is_superuser &&
      state.userProfile.is_active
    )
  },
  loginError: (state) => state.logInError,
  dashboardShowDrawer: (state) => state.dashboardShowDrawer,
  dashboardMiniDrawer: (state) => state.dashboardMiniDrawer,
  userProfile: (state) => state.userProfile,
  token: (state) => state.token,
  isLoggedIn: (state) => state.isLoggedIn,
  firstNotification: (state) =>
    state.notifications.length > 0 && state.notifications[0],
}
