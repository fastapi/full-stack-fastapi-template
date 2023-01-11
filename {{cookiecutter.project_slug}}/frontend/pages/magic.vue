<template>
    <main class="flex min-h-full">
      <div class="flex flex-1 flex-col justify-center py-12 px-4 sm:px-6 lg:flex-none lg:px-20 xl:px-24">
        <div class="mx-auto w-full max-w-sm lg:w-96">
          <div>
            <component 
              :is="EnvelopeIcon" 
              class="text-rose-500 h-12 w-12" aria-hidden="true" 
            />
            <h2 class="mt-6 text-3xl font-bold tracking-tight text-gray-900">Check your email</h2>
            <p class="text-sm font-medium text-rose-500 hover:text-rose-600 mt-6">
              We sent you an email with a magic link. Once you click that (or copy it into this browser) you'll be 
              signed in.
            </p>
            <p class="text-sm font-medium text-rose-500 hover:text-rose-600 mt-2">
              Make sure you use the same browser you requested the login from or it won't work.
            </p>
          </div>

          <NuxtLink to="/login?oauth=true" class="mt-8 flex">
            <component 
              :is="LinkIcon" 
              class="text-rose-500 h-4 w-4 mr-1" aria-hidden="true" 
            />
            <p class="text-sm text-rose-500 align-middle">
              If you prefer, use your password & don't email.
            </p>
          </NuxtLink>
        </div>
      </div>
      <div class="relative hidden w-0 flex-1 lg:block">
        <img class="absolute inset-0 h-full w-full object-cover" src="https://images.unsplash.com/photo-1561487138-99ccf59b135c?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=764&q=80" alt="" />
      </div>
    </main>
</template>

<script setup lang="ts">
import { LinkIcon, EnvelopeIcon } from "@heroicons/vue/24/outline"
import { useAuthStore } from "@/stores"
import { tokenParser } from "@/utilities"

definePageMeta({
  layout: "authentication",
  middleware: ["anonymous"],
});

const auth = useAuthStore()
const redirectRoute = "/login"


onMounted(async () => {
  if (!tokenParser(auth.authTokens.token).hasOwnProperty("fingerprint")) {
    return await navigateTo(redirectRoute)    
  }
})
</script>