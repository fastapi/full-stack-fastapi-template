<template>
  <div class="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
    <div class="bg-white shadow overflow-hidden sm:rounded-lg">
      <ValidationObserver>
        <form action="#" method="POST">
          <div class="shadow overflow-hidden rounded-md">
            <div class="px-4 py-5 bg-white sm:p-6">
              <div class="grid grid-cols-6 gap-6">
                <div class="col-span-6 sm:col-span-4">
                  <ValidationProvider
                    v-slot="{ errors }"
                    rules="confirmed:confirmation"
                  >
                    <label
                      for="password1"
                      class="block text-sm font-medium text-gray-700"
                      >New password</label
                    >
                    <input
                      id="password1"
                      v-model="password1"
                      name="password"
                      type="password"
                      autocomplete="current-password"
                      required
                      class="inpt"
                    />
                    <span
                      class="block px-3 py-2 text-sm font-light text-gray-700"
                      >{{ errors[0] }}</span
                    >
                  </ValidationProvider>
                </div>

                <div class="col-span-6 sm:col-span-4">
                  <label
                    for="password2"
                    class="block text-sm font-medium text-gray-700"
                    >Confirm password</label
                  >
                  <ValidationProvider v-slot="{ errors }" vid="confirmation">
                    <input
                      id="password2"
                      v-model="password2"
                      name="confirm-password"
                      type="password"
                      autocomplete="current-password"
                      required
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
      </ValidationObserver>
    </div>
  </div>
</template>

<script lang="ts">
import { Action, Component, Vue } from "nuxt-property-decorator"
import { IUserProfileUpdate } from "@/interfaces"

@Component({
  middleware: "authenticated",
})
export default class UserProfileEditPassword extends Vue {
  @Action("main/updateUserProfile") updateUserProfile
  public password1 = ""
  public password2 = ""

  public cancel() {
    this.$router.back()
  }

  public async submit() {
    const updatedProfile: IUserProfileUpdate = {}
    updatedProfile.password = this.password1
    await this.updateUserProfile(updatedProfile)
    this.$router.push("/main/profile")
  }

  asyncData({ store }) {
    store.commit("helpers/setHeadingTitle", "Dashboard - Change Password")
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
