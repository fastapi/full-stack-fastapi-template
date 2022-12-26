import { useAuthStore } from "@/stores"

export default defineNuxtRouteMiddleware((to, from) => {
  const auth = useAuthStore()
  if (!auth.isAdmin) {
    return abortNavigation()
  }  
})