export default {
  adminUsers: (state) => state.users,
  adminOneUser: (state) => (userId: number) => {
    const filteredUsers = state.users.filter((user) => user.id === userId)
    if (filteredUsers.length > 0) {
      return { ...filteredUsers[0] }
    }
  },
}
