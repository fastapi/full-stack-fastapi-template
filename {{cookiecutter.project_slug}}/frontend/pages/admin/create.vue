<template>
  <div class="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
    <div class="bg-white shadow overflow-hidden sm:rounded-lg">
      <ValidationObserver>
        <form>
          <div class="shadow overflow-hidden rounded-md">
            <div class="px-4 py-5 bg-white sm:p-6">
              <div class="grid grid-cols-6 gap-6">
                <div class="col-span-6 sm:col-span-4">
                  <label for="full_name" class="lgnd">Full name</label>
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
                  <label for="email_address" class="lgnd">Email address</label>
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

                <div class="-mt-4 col-span-6 sm:col-span-4">
                  <fieldset>
                    <legend class="lgnd">User authorisation and status</legend>
                    <div class="mt-4 space-y-4">
                      <div class="flex items-start">
                        <div class="flex items-center h-5">
                          <input
                            id="isActive"
                            v-model="isActive"
                            name="isActive"
                            type="checkbox"
                            class="focus:ring-indigo-500 h-4 w-4 text-indigo-600 border-gray-300 rounded"
                          />
                        </div>
                        <div class="ml-3 text-sm">
                          <label
                            for="isActive"
                            class="font-medium text-gray-700"
                            >is Active</label
                          >
                          <p class="text-gray-500">
                            Set user status as 'active'.
                          </p>
                        </div>
                      </div>
                      <div class="flex items-start">
                        <div class="flex items-center h-5">
                          <input
                            id="isSuperuser"
                            v-model="isSuperuser"
                            name="isSuperuser"
                            type="checkbox"
                            class="focus:ring-indigo-500 h-4 w-4 text-indigo-600 border-gray-300 rounded"
                          />
                        </div>
                        <div class="ml-3 text-sm">
                          <label
                            for="isSuperuser"
                            class="font-medium text-gray-700"
                            >is Superuser</label
                          >
                          <p class="text-gray-500">
                            Assign user administrative rights.
                          </p>
                        </div>
                      </div>
                    </div>
                  </fieldset>
                </div>

                <div class="col-span-6 sm:col-span-4">
                  <div class="col-span-6 sm:col-span-4">
                    <ValidationProvider
                      v-slot="{ errors }"
                      rules="confirmed:password2"
                    >
                      <label for="password1" class="lgnd">New password</label>
                      <input
                        id="password1"
                        v-model="password1"
                        name="password1"
                        type="password"
                        required
                        autocomplete="current-password"
                        class="inpt"
                      />
                      <span
                        class="block px-3 py-2 text-sm font-light text-gray-700"
                        >{{ errors[0] }}</span
                      >
                    </ValidationProvider>
                  </div>

                  <div class="col-span-6 sm:col-span-4">
                    <label for="password2" class="lgnd">Confirm password</label>
                    <ValidationProvider v-slot="{ errors }" vid="password2">
                      <input
                        id="password2"
                        v-model="password2"
                        name="password2"
                        type="password"
                        required
                        autocomplete="current-password"
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
                Create
              </button>
            </div>
          </div>
        </form>
      </ValidationObserver>
    </div>
  </div>
</template>

<script lang="ts">
import { Component, Vue, Action } from "nuxt-property-decorator"
import { IUserProfileCreate } from "@/interfaces"

@Component({
  middleware: "has-admin-access",
})
export default class AdminEditUser extends Vue {
  @Action("admin/createUser") createUser
  public fullName: string = ""
  public email: string = ""
  public isActive: boolean = true
  public isSuperuser: boolean = false
  public setPassword: boolean = false
  public password1: string = ""
  public password2: string = ""

  public reset() {
    this.password1 = ""
    this.password2 = ""
    this.fullName = ""
    this.email = ""
    this.isActive = true
    this.isSuperuser = false
  }

  public cancel() {
    this.$router.back()
  }

  public async submit() {
    const createdProfile: IUserProfileCreate = {
      email: this.email,
    }
    if (this.fullName) {
      createdProfile.full_name = this.fullName
    }
    if (this.email) {
      createdProfile.email = this.email
    }
    createdProfile.is_active = this.isActive
    createdProfile.is_superuser = this.isSuperuser
    createdProfile.password = this.password1
    await this.createUser(createdProfile)
    this.$router.push("/admin")
  }

  asyncData({ store }) {
    store.commit("helpers/setHeadingTitle", "Administration - Create User")
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
.lgnd {
  @apply block text-sm font-light text-gray-700;
}
</style>
