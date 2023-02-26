<template>
  <div v-if="!auth.loggedIn" class="py-12 sm:py-20">
    <div class="mx-auto max-w-7xl sm:px-6 lg:px-8">
      <div
        class="relative isolate flex flex-col gap-10 overflow-hidden bg-gray-900 px-6 py-16 shadow-2xl sm:rounded-xl sm:px-24 xl:flex-row xl:items-center xl:py-20">
        <h2 class="max-w-2xl text-3xl font-bold tracking-tight text-white sm:text-4xl xl:max-w-none xl:flex-auto">
          {{ props.cardText }}</h2>
        <Form @submit="submit" :validation-schema="schema" class="w-full max-w-md">
          <div class="flex gap-x-4">
            <label for="email-address" class="sr-only">Email address</label>
            <Field id="email" name="email" type="email" autocomplete="email" placeholder="Enter your email"
              class="min-w-0 flex-auto rounded-md border-0 bg-white/5 px-3.5 py-2 text-white shadow-sm ring-1 ring-inset ring-white/10 focus:ring-2 focus:ring-inset focus:ring-white sm:text-sm sm:leading-6" />
            <ErrorMessage name="email"
              class="absolute left-5 top-5 translate-y-full w-48 px-2 py-1 bg-gray-700 rounded-lg text-center text-white text-sm after:content-[''] after:absolute after:left-1/2 after:bottom-[100%] after:-translate-x-1/2 after:border-8 after:border-x-transparent after:border-t-transparent after:border-b-gray-700" />
            <button type="submit"
              class="flex-none rounded-md bg-white py-2.5 px-3.5 text-sm font-semibold text-gray-900 shadow-sm hover:bg-gray-100 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-white">
              Sign-up
            </button>
          </div>
          <p class="mt-4 text-sm leading-6 text-gray-300">We care about your data. Read our <NuxtLink to="/privacy"
              class="font-semibold text-white">privacy policy</NuxtLink>.</p>
        </Form>
        <svg viewBox="0 0 1024 1024" class="absolute top-1/2 left-1/2 -z-10 h-[64rem] w-[64rem] -translate-x-1/2"
          aria-hidden="true">
          <circle cx="512" cy="512" r="512" fill="url(#759c1415-0410-454c-8f7c-9a820de03641)" fill-opacity="0.7" />
          <defs>
            <radialGradient id="759c1415-0410-454c-8f7c-9a820de03641" cx="0" cy="0" r="1" gradientUnits="userSpaceOnUse"
              gradientTransform="translate(512 512) rotate(90) scale(512)">
              <stop stop-color="#932122" />
              <stop offset="1" stop-color="#fbcdcd" stop-opacity="0" />
            </radialGradient>
          </defs>
        </svg>
      </div>
    </div>
  </div>
</template>
  
<script setup lang="ts">
import { useAuthStore } from "@/stores"
import { tokenParser, tokenIsTOTP } from "@/utilities"

const props = defineProps({
  cardText: String
})

const auth = useAuthStore()
const redirectAfterMagic = "/magic"
const redirectTOTP = "/totp"

const schema = {
  email: { email: true, required: true },
  password: { min: 8, max: 64 },
}

async function submit(values: any) {
  await auth.logIn({ username: values.email, password: values.password })
  if (auth.authTokens.token && tokenIsTOTP(auth.authTokens.token))
    return await navigateTo(redirectTOTP)
  if (auth.authTokens.token &&
    tokenParser(auth.authTokens.token).hasOwnProperty("fingerprint"))
    return await navigateTo(redirectAfterMagic)
}
</script>