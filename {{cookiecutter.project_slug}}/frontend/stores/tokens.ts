import { ITokenResponse, IWebToken } from "@/interfaces"
import { apiAuth } from "@/api"
import { tokenExpired, tokenParser } from "@/utilities"
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
    async getTokens(payload: { username: string; password?: string }) {
      // https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Operators/Destructuring_assignment
      let response
      try {
        if (payload.password !== undefined) (
          { data: response } = await apiAuth.loginWithOauth(
            payload.username,
            payload.password
          ))
        else (
          { data: response } = await apiAuth.loginWithMagicLink(
            payload.username
          ))
        if (response.value) {
          if (response.value.hasOwnProperty("claim")) this.setMagicToken(response.value as unknown as IWebToken)
          else this.setTokens(response.value as unknown as ITokenResponse)          
        } else throw "Error"
      } catch (error) {
        toasts.addNotice({
          title: "Login error",
          content: "Please check your details, or internet connection, and try again.",
          icon: "error"
        })
        this.deleteTokens()
      }
    },
    async validateMagicTokens(token: string) {
      try {
        const data: string = this.token
        // Check the two magic tokens meet basic criteria
        const localClaim = tokenParser(data)
        const magicClaim = tokenParser(token)
        if (localClaim.hasOwnProperty("fingerprint") 
            && magicClaim.hasOwnProperty("fingerprint")
            && localClaim["fingerprint"] === magicClaim["fingerprint"]) {
          const { data: response } = await apiAuth.validateMagicLink(
            token, { "claim": data }
          )
          if (response.value) {
            this.setTokens(response.value as unknown as ITokenResponse)          
          } else throw "Error"
        }
      } catch (error) {
        toasts.addNotice({
          title: "Login error",
          content: "Ensure you're using the same browser and that the token hasn't expired.",
          icon: "error"
        })
        this.deleteTokens()
      }
    },
    async validateTOTPClaim(data: string) {
      try {
        const { data: response } = await apiAuth.loginWithTOTP(
          this.access_token, { "claim": data }
        )
        if (response.value) {
          this.setTokens(response.value as unknown as ITokenResponse)          
        } else throw "Error"
      } catch (error) {
        toasts.addNotice({
          title: "Two-factor error",
          content: "Unable to validate your verification code. Make sure it is the latest.",
          icon: "error"
        })
        this.deleteTokens()
      }
    },
    setMagicToken(payload: IWebToken) {
      this.access_token = payload.claim
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