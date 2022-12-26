import { useAuthStore } from "@/stores"

export default defineNuxtRouteMiddleware(async (to, from) => {
  const auth = useAuthStore()
  if (!auth.loggedIn) {
    await auth.getUserProfile()
  }
})