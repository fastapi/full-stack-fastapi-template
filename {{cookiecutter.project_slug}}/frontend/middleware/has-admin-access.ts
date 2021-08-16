export default function ({ store, redirect }) {
  if (
    !store.getters["main/hasAdminAccess"] &&
    !store.getters["main/isLoggedIn"]
  ) {
    return redirect("/")
  }
}
