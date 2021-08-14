export default function ({ store, redirect }) {
  if (!store.getters["main/isLoggedIn"]) {
    return redirect("/login")
  }
}
