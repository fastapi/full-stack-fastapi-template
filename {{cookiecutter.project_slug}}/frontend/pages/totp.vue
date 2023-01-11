<template>
  <main class="flex min-h-full">
    <div class="flex flex-1 flex-col justify-center py-12 px-4 sm:px-6 lg:flex-none lg:px-20 xl:px-24">
      <div class="mx-auto w-full max-w-sm lg:w-96">
        <div>
          <img class="h-12 w-auto" src="https://tailwindui.com/img/logos/mark.svg?color=rose&shade=500" alt="Your Company" />
          <h2 class="mt-6 text-3xl font-bold tracking-tight text-gray-900">Two-factor authentication</h2>
          <p class="text-sm font-medium text-rose-500 hover:text-rose-600 mt-6">
            Enter the 6-digit verification code from your app.
          </p>
        </div>

        <div class="mt-8">
          <div class="mt-6">
            <Form @submit="submit" :validation-schema="schema" class="space-y-6">
              <div>
                <label for="claim" class="block text-sm font-medium text-gray-700">Verification code</label>
                <div class="mt-1 group relative inline-block w-full">
                  <Field id="claim" name="claim" type="text" autocomplete="off" class="block w-full appearance-none rounded-md border border-gray-300 px-3 py-2 placeholder-gray-400 shadow-sm focus:border-rose-600 focus:outline-none focus:ring-rose-600 sm:text-sm" />
                </div>
              </div>

              <div>
                <button type="submit" class="flex w-full justify-center rounded-md border border-transparent bg-rose-500 py-2 px-4 text-sm font-medium text-white shadow-sm hover:bg-rose-700 focus:outline-none focus:ring-2 focus:ring-rose-600 focus:ring-offset-2">
                  Submit
                </button>
              </div>
            </Form>
          </div>
        </div>
      </div>
    </div>
    <div class="relative hidden w-0 flex-1 lg:block">
      <img class="absolute inset-0 h-full w-full object-cover" src="https://images.unsplash.com/photo-1561487138-99ccf59b135c?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=764&q=80" alt="" />
    </div>
  </main>
</template>

<script setup lang="ts">
import { useAuthStore } from "@/stores"
import { tokenIsTOTP } from "@/utilities"

definePageMeta({
layout: "authentication",
middleware: ["anonymous"],
});

const auth = useAuthStore()
const redirectRoute = "/"
const schema = {
  claim: { required: true, min: 6, max: 7 }
}

async function submit(values: any) {
  await auth.totpLogin(values.claim)
  if (auth.loggedIn) {
    return await navigateTo(redirectRoute)     
  }
}

onMounted(async () => {
  // Check if token exists
  if (!auth.authTokens.token || !tokenIsTOTP(auth.authTokens.token)) 
    return await navigateTo("/")
})
</script>