import { ITokenResponse } from "@/interfaces"
import { apiAuth } from "@/api"
import { tokenExpired } from "@/utilities"
import { useToastStore } from "./toasts"

const toasts = useToastStore()

export const useTokenStore = defineStore("tokens", {
  state: (): ITokenResponse => ({
    access_token: "",
    refresh_token: "",
    token_type: ""
  }),
  persist: true,
  getters: {
    token: (state) => state.access_token,
    refresh: (state) => state.refresh_token
  },
  actions: {
    async getTokens(payload: { username: string; password: string }) {
      try {
        const { data: response } = await apiAuth.logInGetToken(
          payload.username,
          payload.password
        )
        if (response.value) this.setTokens(response.value as unknown as ITokenResponse)
        else toasts.addNotice({
          title: "Login error",
          content: "Please check your details, or internet connection, and try again.",
          icon: "error"
        })
      } catch (error) {
        toasts.addNotice({
          title: "Login error",
          content: "Please check your details, or internet connection, and try again.",
          icon: "error"
        })
        this.deleteTokens()
      }
    },
    setTokens (payload: ITokenResponse) {
      this.access_token = payload.access_token
      this.refresh_token = payload.refresh_token
      this.token_type = payload.token_type
    },
    async refreshTokens() {
      let hasExpired = this.token ? tokenExpired(this.token) : true
      if (hasExpired) {
        hasExpired = this.refresh ? tokenExpired(this.refresh) : true
        if (!hasExpired) {
          try {
            const { data: response } = await apiAuth.getRefreshedToken(this.refresh)
            if (response.value) this.setTokens(response.value)
          } catch (error) {
            this.deleteTokens()
          } 
        } else {
          this.deleteTokens()
        }    
      }
    },
    // reset state using `$reset`
    deleteTokens () {
      this.$reset()
    }
  }
})