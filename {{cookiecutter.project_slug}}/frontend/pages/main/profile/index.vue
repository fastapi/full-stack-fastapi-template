<template>
  <div class="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
    <!-- Replace with your content -->
    <div class="bg-white shadow overflow-hidden sm:rounded-lg">
      <div class="px-4 py-5 sm:px-6">
        <h3 class="text-lg leading-6 font-medium text-gray-900">
          User Profile
        </h3>
        <p class="mt-1 max-w-2xl text-sm text-gray-500">
          Personal details and information.
        </p>
      </div>
      <div class="border-t border-gray-200">
        <dl>
          <div
            class="bg-gray-50 px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6"
          >
            <dt class="text-sm font-medium text-gray-500">Full name</dt>
            <dd
              v-if="userProfile && userProfile.full_name"
              class="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2"
            >
              {{ userProfile.full_name }}
            </dd>
            <dd v-else class="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
              -----
            </dd>
          </div>
          <div
            class="bg-white px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6"
          >
            <dt class="text-sm font-medium text-gray-500">Email address</dt>
            <dd
              v-if="userProfile && userProfile.email"
              class="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2"
            >
              {{ userProfile.email }}
            </dd>
            <dd v-else class="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
              -----
            </dd>
          </div>
          <div
            class="bg-gray-50 px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6"
          >
            <dt class="text-sm font-medium text-gray-500"></dt>
            <dd class="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
              <div
                class="bg-gray-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse"
              >
                <NuxtLink to="/main/profile/edit-password" class="btn"
                  >Change password</NuxtLink
                >
                <NuxtLink to="/main/profile/edit" class="btn"
                  >Edit profile</NuxtLink
                >
              </div>
            </dd>
          </div>
        </dl>
      </div>
    </div>
    <!-- /End replace -->
  </div>
</template>

<script lang="ts">
import { Component, Vue, Getter } from "nuxt-property-decorator"

@Component({
  middleware: "authenticated",
})
export default class UserProfile extends Vue {
  @Getter("main/userProfile") userProfile

  asyncData({ store }) {
    store.commit("helpers/setHeadingTitle", "Dashboard")
  }
}
</script>

<style>
.btn {
  @apply mt-3 w-full inline-flex justify-center rounded-md border border-gray-300 shadow-sm px-4 py-2 bg-white text-base font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 sm:mt-0 sm:ml-3 sm:w-auto sm:text-sm;
}
</style>
