<template>
  <div class="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
    <div class="bg-white shadow overflow-hidden sm:rounded-lg">
      <form action="#" method="POST">
        <div class="shadow overflow-hidden rounded-md">
          <div class="px-4 py-5 bg-white sm:p-6">
            <div class="grid grid-cols-6 gap-6">
              <div class="col-span-6 sm:col-span-4">
                <label
                  for="full_name"
                  class="block text-sm font-medium text-gray-700"
                  >Full name</label
                >
                <input
                  id="full_name"
                  v-model="fullName"
                  type="text"
                  autocomplete="given-name"
                  :placeholder="fullName"
                  class="inpt"
                />
              </div>

              <div class="col-span-6 sm:col-span-4">
                <label
                  for="email_address"
                  class="block text-sm font-medium text-gray-700"
                  >Email address</label
                >
                <ValidationProvider v-slot="{ errors }" rules="email">
                  <input
                    id="email_address"
                    v-model="email"
                    type="text"
                    autocomplete="email"
                    :placeholder="email"
                    class="inpt"
                  />
                  <span
                    class="block px-3 py-2 text-sm font-light text-gray-700"
                    >{{ errors[0] }}</span
                  >
                </ValidationProvider>
              </div>
            </div>
          </div>
          <div class="px-4 py-3 bg-gray-50 text-right sm:px-6">
            <button type="submit" class="btn" @click.prevent="cancel">
              Cancel
            </button>
            <button type="submit" class="btn" @click.prevent="reset">
              Reset
            </button>
            <button
              type="submit"
              class="btn btn-indigo"
              @click.prevent="submit"
            >
              Update
            </button>
          </div>
        </div>
      </form>
    </div>
  </div>
</template>

<script lang="ts">
import { Action, Component, Getter, Vue } from "nuxt-property-decorator"
import { IUserProfileUpdate } from "@/interfaces"

@Component({
  middleware: "authenticated",
})
export default class UserProfileEdit extends Vue {
  @Getter("main/userProfile") userProfile
  @Action("main/updateUserProfile") updateUserProfile
  public fullName: string = ""
  public email: string = ""

  public created() {
    this.reset()
  }

  public reset() {
    if (this.userProfile) {
      this.fullName = this.userProfile.full_name
      this.email = this.userProfile.email
    }
  }

  public cancel() {
    this.$router.back()
  }

  public async submit() {
    const updatedProfile: IUserProfileUpdate = {}
    if (this.fullName) {
      updatedProfile.full_name = this.fullName
    }
    if (this.email) {
      updatedProfile.email = this.email
    }
    await this.updateUserProfile(updatedProfile)
    this.$router.push("/main/profile")
  }

  asyncData({ store }) {
    store.commit("helpers/setHeadingTitle", "Dashboard - Edit Profile")
  }
}
</script>

<style>
.inpt {
  @apply mt-1 relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-md focus:outline-none focus:ring-indigo-300 focus:border-indigo-300 shadow-sm sm:text-sm;
}
.btn {
  @apply mt-3 w-full inline-flex justify-center rounded-md border border-gray-300 shadow-sm px-4 py-2 bg-white text-base font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 sm:mt-0 sm:ml-3 sm:w-auto sm:text-sm;
}
.btn-indigo {
  @apply text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500;
}
</style>
