<template>
  <div class="container mx-auto">
    <div>
      <div
        class="min-h-screen flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8"
      >
        <div class="max-w-md w-full space-y-8">
          <div>
            <img
              class="mx-auto h-12 w-auto"
              src="https://tailwindui.com/img/logos/workflow-mark-indigo-600.svg"
              alt="Workflow"
            />
            <h2 class="mt-6 text-center text-3xl font-extrabold text-gray-900">
              Create your account
            </h2>
          </div>
          <ValidationObserver v-slot="{ invalid }" immediate>
            <form class="mt-8 space-y-6" @submit.prevent="submit">
              <div class="rounded-md shadow-sm -space-y-px">
                <div>
                  <ValidationProvider v-slot="{ failedRules }" rules="email">
                    <label for="email-address" class="sr-only"
                      >Email address</label
                    >
                    <div
                      class="appearance-none rounded-none relative border rounded-t-md border-gray-300 flex w-full"
                    >
                      <span
                        class="inline-flex items-center px-3 py-2 text-sm font-light text-gray-500 bg-gray-50"
                      >
                        <svg
                          v-if="failedRules.email"
                          class="w-5 h-5 text-red-700"
                          xmlns="http://www.w3.org/2000/svg"
                          fill="none"
                          viewBox="0 0 24 24"
                          stroke="currentColor"
                        >
                          <path
                            stroke-linecap="round"
                            stroke-linejoin="round"
                            stroke-width="2"
                            d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
                          />
                        </svg>
                        <svg
                          v-else
                          class="w-5 h-5"
                          xmlns="http://www.w3.org/2000/svg"
                          fill="none"
                          viewBox="0 0 24 24"
                          stroke="currentColor"
                        >
                          <path
                            stroke-linecap="round"
                            stroke-linejoin="round"
                            stroke-width="2"
                            d="M16 12a4 4 0 10-8 0 4 4 0 008 0zm0 0v1.5a2.5 2.5 0 005 0V12a9 9 0 10-9 9m4.5-1.206a8.959 8.959 0 01-4.5 1.207"
                          />
                        </svg>
                      </span>

                      <input
                        id="email-address"
                        v-model="email"
                        name="email"
                        type="email"
                        autocomplete="email"
                        required
                        class="w-full px-3 py-2 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
                        placeholder="Email address"
                        @keyup.enter="submit"
                      />
                    </div>
                  </ValidationProvider>
                </div>
                <div
                  class="appearance-none rounded-none relative rounded-b-md border border-gray-300 flex w-full"
                >
                  <label for="full-name" class="sr-only">Full name</label>
                  <span
                    class="inline-flex items-center px-3 py-2 text-sm font-light text-gray-500 bg-gray-50"
                  >
                    <svg
                      class="w-5 h-5"
                      xmlns="http://www.w3.org/2000/svg"
                      fill="none"
                      viewBox="0 0 24 24"
                      stroke="currentColor"
                    >
                      <path
                        stroke-linecap="round"
                        stroke-linejoin="round"
                        stroke-width="2"
                        d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
                      />
                    </svg>
                  </span>
                  <input
                    id="ful-name"
                    v-model="fullName"
                    name="fullName"
                    type="text"
                    autocomplete="given-name"
                    class="w-full px-3 py-2 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
                    placeholder="Full name"
                    @keyup.enter="submit"
                  />
                </div>
              </div>
              <div class="rounded-md shadow-sm -space-y-px">
                <div>
                  <ValidationProvider
                    v-slot="{ errors }"
                    name="password1"
                    vid="password1"
                    rules="confirmed:password2"
                  >
                    <label for="password1" class="sr-only"
                      >Create password</label
                    >
                    <div
                      class="appearance-none rounded-none relative border rounded-t-md border-gray-300 flex w-full"
                    >
                      <span
                        class="inline-flex items-center px-3 py-2 text-sm font-light text-gray-500 bg-gray-50"
                      >
                        <svg
                          v-if="errors[0] === 'true'"
                          class="w-5 h-5 text-red-700"
                          xmlns="http://www.w3.org/2000/svg"
                          fill="none"
                          viewBox="0 0 24 24"
                          stroke="currentColor"
                        >
                          <path
                            stroke-linecap="round"
                            stroke-linejoin="round"
                            stroke-width="2"
                            d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
                          />
                        </svg>
                        <svg
                          v-else
                          class="w-5 h-5"
                          xmlns="http://www.w3.org/2000/svg"
                          fill="none"
                          viewBox="0 0 24 24"
                          stroke="currentColor"
                        >
                          <path
                            stroke-linecap="round"
                            stroke-linejoin="round"
                            stroke-width="2"
                            d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"
                          />
                        </svg>
                      </span>
                      <input
                        id="password1"
                        v-model="password1"
                        name="password1"
                        type="password"
                        autocomplete="current-password"
                        placeholder="Create password"
                        required
                        class="w-full px-3 py-2 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
                      />
                    </div>
                  </ValidationProvider>
                </div>
                <div>
                  <ValidationProvider
                    v-slot="{ errors }"
                    vid="password2"
                    name="password2"
                  >
                    <label for="password2" class="sr-only"
                      >Confirm password</label
                    >
                    <div
                      class="appearance-none rounded-none relative border rounded-b-md border-gray-300 flex w-full"
                    >
                      <span
                        class="inline-flex items-center px-3 py-2 text-sm font-light text-gray-600 bg-gray-50"
                      >
                        <svg
                          v-if="errors[0] === 'true'"
                          class="w-5 h-5 text-red-700"
                          xmlns="http://www.w3.org/2000/svg"
                          fill="none"
                          viewBox="0 0 24 24"
                          stroke="currentColor"
                        >
                          <path
                            stroke-linecap="round"
                            stroke-linejoin="round"
                            stroke-width="2"
                            d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
                          />
                        </svg>
                        <svg
                          v-else
                          class="w-5 h-5"
                          xmlns="http://www.w3.org/2000/svg"
                          fill="none"
                          viewBox="0 0 24 24"
                          stroke="currentColor"
                        >
                          <path
                            stroke-linecap="round"
                            stroke-linejoin="round"
                            stroke-width="2"
                            d=""
                          />
                        </svg>
                      </span>
                      <input
                        id="password2"
                        v-model="password2"
                        name="password2"
                        type="password"
                        autocomplete="current-password"
                        placeholder="Confirm password"
                        required
                        class="w-full px-3 py-2 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
                      />
                    </div>
                  </ValidationProvider>
                </div>
              </div>

              <div class="text-sm text-right">
                <a
                  href="#"
                  class="font-medium text-right text-indigo-600 hover:text-indigo-500"
                  @click.prevent="cancel"
                >
                  Cancel
                </a>
              </div>

              <div>
                <button
                  type="submit"
                  :disabled="invalid"
                  class="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                >
                  <span
                    class="absolute left-0 inset-y-0 flex items-center pl-3"
                  >
                    <!-- Heroicon name: solid/lock-closed -->
                    <svg
                      class="h-5 w-5 text-indigo-500 group-hover:text-indigo-400"
                      xmlns="http://www.w3.org/2000/svg"
                      viewBox="0 0 20 20"
                      fill="currentColor"
                      aria-hidden="true"
                    >
                      <path
                        fill-rule="evenodd"
                        d="M5 9V7a5 5 0 0110 0v2a2 2 0 012 2v5a2 2 0 01-2 2H5a2 2 0 01-2-2v-5a2 2 0 012-2zm8-2v2H7V7a3 3 0 016 0z"
                        clip-rule="evenodd"
                      />
                    </svg>
                  </span>
                  Register
                </button>
              </div>
            </form>
          </ValidationObserver>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { Action, Component, Vue } from "nuxt-property-decorator"
import { IUserOpenProfileCreate } from "@/interfaces"

@Component({
  middleware: "anonymous",
})
export default class Register extends Vue {
  @Action("main/createUserProfile") createMe
  public fullName: string = ""
  public email: string = ""
  public password1 = ""
  public password2 = ""

  public async submit() {
    const createdProfile: IUserOpenProfileCreate = {
      email: this.email,
      password: this.password1,
    }
    if (this.fullName) {
      createdProfile.full_name = this.fullName
    }
    await this.createMe(createdProfile)
    this.$router.push("/login")
  }

  public cancel() {
    this.$router.back()
  }

  asyncData({ store }) {
    store.commit("helpers/setHeadingTitle", null)
  }
}
</script>
