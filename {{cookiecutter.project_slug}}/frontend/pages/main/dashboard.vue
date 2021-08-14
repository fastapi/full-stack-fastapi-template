<template>
  <div class="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
    <div class="bg-white shadow overflow-hidden sm:rounded-lg">
      <!-- Replace with your content -->
      <p class="m-10 font-semibold text-lg">Welcome {{ greetedUser }}!</p>
      <div class="bg-gray-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse">
        <NuxtLink to="/main/profile" class="btn btn-indigo"
          >View Profile</NuxtLink
        >
        <NuxtLink to="/main/profile/edit" class="btn">Edit profile</NuxtLink>
        <NuxtLink to="/main/profile/edit-password" class="btn"
          >Change password</NuxtLink
        >
      </div>
      <!-- /End replace -->
    </div>
  </div>
</template>

<script lang="ts">
import { Component, Vue, Getter } from "nuxt-property-decorator"

@Component({
  middleware: "authenticated",
})
export default class Dashboard extends Vue {
  @Getter("main/userProfile") userProfile

  get greetedUser() {
    if (this.userProfile) {
      if (this.userProfile.full_name) {
        return this.userProfile.full_name
      } else {
        return this.userProfile.email
      }
    }
  }

  asyncData({ store }) {
    store.commit("helpers/setHeadingTitle", "Dashboard")
  }
}
</script>

<style>
.btn {
  @apply mt-3 w-full inline-flex justify-center rounded-md border border-gray-300 shadow-sm px-4 py-2 bg-white text-base font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 sm:mt-0 sm:ml-3 sm:w-auto sm:text-sm;
}
.btn-indigo {
  @apply text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500;
}
</style>
