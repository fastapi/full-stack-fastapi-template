import {
  IUserProfile,
  IUserProfileUpdate,
  IUserOpenProfileCreate,
} from "@/interfaces"
import { apiAuth } from "@/api"
import { useTokenStore } from "./tokens"
import { useToastStore } from "./toasts"

const toasts = useToastStore()

export const useAuthStore = defineStore("authUser", {
  state: (): IUserProfile => ({
    id: "",
    email: "",
    email_validated: false,
    is_active: false,
    is_superuser: false,
    full_name: ""
  }),
  persist: true,
  getters: {
    isAdmin: (state) => {
        return (
          state.id &&
          state.is_superuser &&
          state.is_active
        )
    },
    profile: (state) => state,
    loggedIn: (state) => state.id !== "",
    authTokens: () => {
      return ( useTokenStore() )
    }
  },
  actions: {
    async logIn(payload: { username: string; password: string }) {
      try {
        await this.authTokens.getTokens(payload)       
        await this.getUserProfile()
      } catch (error) {
        toasts.addNotice({
          title: "Login error",
          content: "Please check your details, or internet connection, and try again.",
          icon: "error"
        })
        this.logOut()
      }
    },
    async createUserProfile(payload: IUserOpenProfileCreate) {
      try {
        const { data: response } = await apiAuth.createProfile(payload)
        if (response.value) this.setUserProfile(response.value)
        await this.authTokens.getTokens({ 
          username: this.email, 
          password: payload.password 
        })
      } catch (error) {
        toasts.addNotice({
          title: "Login creation error",
          content: "Please check your details, or internet connection, and try again.",
          icon: "error"
        })
      }
    },
    async getUserProfile() {
      if (!this.loggedIn) {
        await this.authTokens.refreshTokens()
        if (this.authTokens.token) {
          try {
            const { data: response } = await apiAuth.getProfile(this.authTokens.token)
            if (response.value) this.setUserProfile(response.value)
          } catch (error) {
            this.logOut()
          }
        }
      }
    },
    async updateUserProfile(payload: IUserProfileUpdate) {
      await this.authTokens.refreshTokens()
      if (this.loggedIn && this.authTokens.token) {
        try {
          const { data: response } = await apiAuth.updateProfile(this.authTokens.token, payload)
          if (response.value) this.setUserProfile(response.value)
        } catch (error) {
          toasts.addNotice({
            title: "Profile update error",
            content: "Please check your submission, or internet connection, and try again.",
            icon: "error"
          })
        }
      }
    },
    // mutations are actions, instead of `state` as first argument use `this`
    setUserProfile (payload: IUserProfile) {
      this.id = payload.id
      this.email = payload.email
      this.email_validated = payload.email_validated
      this.is_active = payload.is_active
      this.is_superuser = payload.is_superuser
      this.full_name = payload.full_name
    },
    async sendEmailValidation() {
      await this.authTokens.refreshTokens()
      if (this.authTokens.token && !this.email_validated) {
        try {
          const { data: response } = await apiAuth.requestValidationEmail(this.authTokens.token)
          if (response.value) {
            toasts.addNotice({
              title: "Validation sent",
              content: response.value.msg,
            })
          }
        } catch (error) {
          toasts.addNotice({
            title: "Validation error",
            content: "Please check your email and try again.",
            icon: "error"
          })
        }
      }
    },
    async validateEmail(validationToken: string) {
      await this.authTokens.refreshTokens()
      if (this.authTokens.token && !this.email_validated) {
        try {
          const { data: response } = await apiAuth.validateEmail(
            this.authTokens.token,
            validationToken
          )
          if (response.value) {
            this.email_validated = true
            if (response.value) {
              toasts.addNotice({
                title: "Success",
                content: response.value.msg,
              })
            }
          }
        } catch (error) {
          toasts.addNotice({
            title: "Validation error",
            content: "Invalid token. Check your email and resend validation.",
            icon: "error"
          })
        }
      }
    },
    async recoverPassword(email: string) {
      if (!this.loggedIn) {
        try {
          const { data: response } = await apiAuth.recoverPassword(email)
          toasts.addNotice({
            title: "Success",
            content: response.value 
              ? response.value.msg 
              : "Password validation email sent. Check your email and respond.",
          })
        } catch (error) {
          toasts.addNotice({
            title: "Recovery error",
            content: "Check your email and retry.",
            icon: "error"
          })
        }
      }
    },
    async resetPassword(password: string, token: string) {
      if (!this.loggedIn) {
        try {
          const { data: response } = await apiAuth.resetPassword(password, token)
          if (response.value) toasts.addNotice({
            title: "Success",
            content: response.value.msg,
          })
          else throw "Error"
        } catch (error) {
          toasts.addNotice({
            title: "Reset error",
            content: "There was a problem. Please retry.",
            icon: "error"
          })
        }
      }
    },
    // reset state using `$reset`
    logOut () {
      this.authTokens.deleteTokens()
      this.$reset()
    }
  }
})