<template>
    <main>
      <!-- Hero section -->
      <div class="overflow-hidden pt-8 sm:pt-12 lg:relative lg:py-48">
        <div class="mx-auto max-w-md px-4 sm:max-w-3xl sm:px-6 lg:grid lg:max-w-7xl lg:grid-cols-2 lg:gap-24 lg:px-8">
          <div>
            <div class="mt-10">
              <div>
                <div class="inline-flex space-x-4">
                  <NuxtLink to="/about" class="rounded bg-rose-50 px-2.5 py-1 text-sm font-semibold text-rose-500">Key features</NuxtLink>
                  <a :href="github.href" class="inline-flex space-x-4">
                    <span class="inline-flex items-center space-x-1 text-sm font-medium text-rose-500">
                      <span class="inline-flex items-center space-x-1 text-sm font-medium text-rose-400">
                        <component :is="github.icon" class="h-5 w-5" aria-hidden="true" />
                      </span>
                      <span>Source repository</span>
                      <ChevronRightIcon class="h-5 w-5" aria-hidden="true" />
                    </span>
                  </a>
                </div>
              </div>
              <div class="mt-6 sm:max-w-xl">
                <h1 class="text-4xl font-bold tracking-tight text-gray-900 sm:text-5xl">FastAPI/Nuxt starter stack</h1>
                <p class="mt-6 text-xl text-gray-500">Accelerate your next web development project with this FastAPI 0.88 / Nuxt.js 3.0 base project generator.</p>
              </div>
              <div class="mt-6 sm:max-w-xl">
                <ul class="list-disc ml-6 text-gray-600">
                  <li>
                    <span class="font-bold">Authentication</span> user management schemas, models, crud and apis, with 
                    OAuth2 JWT token `access` and `refresh` support & default hashing.
                  </li>
                  <li>
                    <span class="font-bold">Authorisation</span> via middleware for page access, including logged in or superuser.
                  </li>
                  <li>
                    <span class="font-bold">Databases</span> for Neo4j and PostgreSQL included, plus PGAdmin for PostgreSQL management, using SQLAlchemy 1.4.
                  </li>
                  <li>
                    <span class="font-bold">Form validation</span> with Vee-Validate 4.
                  </li>
                  <li>
                    <span class="font-bold">State management</span> with Pinia, and persistance with Pinia PersistedState.
                  </li>
                  <li>
                    <span class="font-bold">CSS and templates</span> with TailwindCSS, HeroIcons, and HeadlessUI.
                  </li>
                  <li>
                    <span class="font-bold">Content management</span> with Nuxt Content for writing Markdown pages.
                  </li>
                </ul>
              </div>
            </div>
          </div>
        </div>

        <div class="sm:mx-auto sm:max-w-3xl sm:px-6">
          <div class="py-12 sm:relative sm:mt-12 sm:py-16 lg:absolute lg:inset-y-0 lg:right-0 lg:w-1/2">
            <div class="hidden sm:block">
              <div class="absolute inset-y-0 left-1/2 w-screen rounded-l-3xl bg-gray-50 lg:left-80 lg:right-0 lg:w-full" />
              <svg class="absolute top-8 right-1/2 -mr-3 lg:left-0 lg:m-0" width="404" height="392" fill="none" viewBox="0 0 404 392">
                <defs>
                  <pattern id="837c3e70-6c3a-44e6-8854-cc48c737b659" x="0" y="0" width="20" height="20" patternUnits="userSpaceOnUse">
                    <rect x="0" y="0" width="4" height="4" class="text-gray-200" fill="currentColor" />
                  </pattern>
                </defs>
                <rect width="404" height="392" fill="url(#837c3e70-6c3a-44e6-8854-cc48c737b659)" />
              </svg>
            </div>
            <div class="relative -mr-40 pl-4 sm:mx-auto sm:max-w-3xl sm:px-0 lg:h-full lg:max-w-none lg:pl-12">
              <img class="w-full rounded-md shadow-xl ring-1 ring-black ring-opacity-5 lg:h-full lg:w-auto lg:max-w-none" src="https://images.unsplash.com/photo-1465661668481-15b9405ca28e?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&flip=h&w=1074&q=80" alt="" />
            </div>
          </div>
        </div>
      </div>
    </main>
</template>

<script setup lang="ts">
import { ChevronRightIcon } from "@heroicons/vue/20/solid"
import { useAuthStore } from "@/stores"
import { tokenIsTOTP } from "@/utilities"

definePageMeta({
  layout: "home",
});

const redirectTOTP = "/totp"
const redirectAfterLogin = "/"
const github = {
  name: "GitHub",
  href: "https://github.com/whythawk/full-stack-fastapi-postgresql",
  icon: defineComponent({
    render: () =>
      h("svg", { fill: "currentColor", viewBox: "0 0 24 24" }, [
        h("path", {
          "fill-rule": "evenodd",
          d: "M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z",
          "clip-rule": "evenodd",
        }),
      ]),
  }),
}

onMounted(async () => {
  // Check if email is being validated
  const route = useRoute()
  const auth = useAuthStore()
  if (route.query && route.query.magic) {
    // No idea: https://stackoverflow.com/q/74759799/295606
    await new Promise((resolve) => {
      setTimeout(() => {
        resolve(true)
      }, 100)
    })
    if (!auth.loggedIn) await auth.magicLogin(route.query.magic as string)
    if (tokenIsTOTP(auth.authTokens.token)) await navigateTo(redirectTOTP)
    else await navigateTo(redirectAfterLogin) 
  }
})
</script>