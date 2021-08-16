import { IUserProfile } from "@/interfaces"

export default {
  setUsers(state, payload: IUserProfile[]) {
    state.users = payload
  },
  setUser(state, payload: IUserProfile) {
    const users = state.users.filter(
      (user: IUserProfile) => user.id !== payload.id
    )
    users.push(payload)
    state.users = users
  },
}
