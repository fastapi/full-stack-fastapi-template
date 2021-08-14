<template>
  <div class="container mx-auto">
    <!-- https://blog.lichter.io/posts/vue-hydration-error/ -->
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
              Reset your password
            </h2>
          </div>

          <ValidationObserver v-slot="{ invalid }" immediate>
            <form class="mt-8 space-y-6" @submit.prevent="submit">
              <div class="rounded-md shadow-sm -space-y-px">
                <div>
                  <ValidationProvider
                    v-slot="{ errors }"
                    name="password1"
                    vid="password1"
                    rules="confirmed:password2"
                  >
                    <label for="password1" class="sr-only">New password</label>
                    <div
                      class="appearance-none rounded-none relative border rounded-t-md border-gray-300 flex w-full"
                    >
                      <span
                        class="inline-flex items-center px-3 py-2 text-sm font-light text-gray-700 bg-gray-50"
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
                        placeholder="New password"
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
                        class="inline-flex items-center px-3 py-2 text-sm font-light text-gray-700 bg-gray-50"
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
              <div>
                <button
                  type="submit"
                  class="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                  :disabled="invalid"
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
                  Reset
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

@Component({
  middleware: "anonymous",
})
export default class ResetPassword extends Vue {
  @Action("main/resetPassword") resetPassword
  public password1 = ""
  public password2 = ""

  public async submit() {
    await this.resetPassword({
      token: this.$route.query.token as string,
      password: this.password1,
    })
    this.$router.push("/")
  }

  asyncData({ store, redirect, query }) {
    store.commit("helpers/setHeadingTitle", null)
    const token = query.token as string
    if (!token) {
      store.commit("main/addNotification", {
        content: "No token provided, start a new password recovery",
        color: "error",
      })
      redirect("/recover-password")
    }
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
