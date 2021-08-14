import { IUserProfile } from "@/interfaces"

export interface AppNotification {
  content: string
  color?: string
  showProgress?: boolean
}

export interface MainState {
  token: string
  isLoggedIn: boolean | null
  logInError: boolean
  userProfile: IUserProfile | null
  notifications: AppNotification[]
}

const defaultState: MainState = {
  isLoggedIn: null,
  token: "",
  logInError: false,
  userProfile: null,
  notifications: [],
}

export default () => defaultState
