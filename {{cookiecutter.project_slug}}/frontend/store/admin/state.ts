import { IUserProfile } from "@/interfaces"

export interface AdminState {
  users: IUserProfile[]
}

const defaultState: AdminState = {
  users: [],
}

export default () => defaultState
