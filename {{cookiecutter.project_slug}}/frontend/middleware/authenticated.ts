import { useAuthStore } from "@/stores"

export default defineNuxtRouteMiddleware((to, from) => {
  const auth = useAuthStore()
  const routes = ["/login", "/join", "/recover-password", "/reset-password"]
  if (!auth.loggedIn) {
    if (routes.includes(from.path)) return navigateTo("/")
    else return abortNavigation()
  }
})