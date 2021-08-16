<template>
  <div class="sm:text-center lg:text-left">
    <h1
      class="text-4xl tracking-tight font-extrabold text-gray-900 sm:text-4xl md:text-5xl"
    >
      <span class="block xl:inline">Nuxt.js</span>
      <span class="block text-indigo-600 xl:inline">frontend</span>
    </h1>
    <p
      class="mt-3 text-base text-gray-500 sm:mt-5 sm:text-lg sm:max-w-xl sm:mx-auto md:mt-5 md:text-xl lg:mx-0"
    >
      Drop-in replacement for Vue.js
      <a
        href="https://github.com/tiangolo/full-stack-fastapi-postgresql"
        target="_blank"
        rel="noopener noreferrer"
        class="text-indigo-600 hover:text-indigo-500"
        >FastAPI base project generator</a
      >.
    </p>
    <div class="mt-10">
      <dl
        class="space-y-10 md:space-y-0 md:grid md:grid-cols-2 md:gap-x-8 md:gap-y-10"
      >
        <div class="relative">
          <dt>
            <div
              class="absolute flex items-center justify-center h-12 w-12 rounded-md bg-indigo-500 text-white"
            >
              <img
                class="h-6 w-6"
                src="https://nuxtjs.org/logos/nuxt-square-white.svg"
              />
            </div>
            <p class="ml-16 text-lg leading-6 font-medium text-gray-900">
              Nuxt.js
            </p>
          </dt>
          <dd class="mt-2 ml-16 text-base text-gray-500">
            <a
              href="https://nuxtjs.org/"
              target="_blank"
              rel="noopener noreferrer"
              class="text-indigo-600 hover:text-indigo-500"
              >Framework</a
            >
            and
            <a
              href="https://github.com/nuxt-community/nuxt-property-decorator"
              target="_blank"
              rel="noopener noreferrer"
              class="text-indigo-600 hover:text-indigo-500"
              >component / property decorator</a
            >.
          </dd>
        </div>

        <div class="relative">
          <dt>
            <div
              class="absolute flex items-center justify-center h-12 w-12 rounded-md bg-indigo-500 text-white"
            >
              <img
                class="h-6 w-6"
                src="https://tailwindui.com/img/logos/workflow-mark-white.svg"
              />
            </div>
            <p class="ml-16 text-lg leading-6 font-medium text-gray-900">
              Tailwind
            </p>
          </dt>
          <dd class="mt-2 ml-16 text-base text-gray-500">
            <a
              href="https://tailwindcss.com/"
              target="_blank"
              rel="noopener noreferrer"
              class="text-indigo-600 hover:text-indigo-500"
              >CSS</a
            >,
            <a
              href="https://heroicons.com/"
              target="_blank"
              rel="noopener noreferrer"
              class="text-indigo-600 hover:text-indigo-500"
              >HeroIcons</a
            >
            and Article content
            <a
              href="https://github.com/tailwindlabs/tailwindcss-typography"
              target="_blank"
              rel="noopener noreferrer"
              class="text-indigo-600 hover:text-indigo-500"
              >typography</a
            >.
          </dd>
        </div>

        <div class="relative">
          <dt>
            <div
              class="absolute flex items-center justify-center h-12 w-12 rounded-md bg-indigo-500 text-white"
            >
              <!-- Heroicon name: outline/lightning-bolt -->
              <svg
                class="h-6 w-6"
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
                aria-hidden="true"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M13 10V3L4 14h7v7l9-11h-7z"
                />
              </svg>
            </div>
            <p class="ml-16 text-lg leading-6 font-medium text-gray-900">
              Helpers
            </p>
          </dt>
          <dd class="mt-2 ml-16 text-base text-gray-500">
            <a
              href="https://github.com/nuxt-community/nuxt-property-decorator"
              target="_blank"
              rel="noopener noreferrer"
              class="text-indigo-600 hover:text-indigo-500"
              >Markdown content</a
            >,
            <a
              href="https://vee-validate.logaretm.com/v3/"
              target="_blank"
              rel="noopener noreferrer"
              class="text-indigo-600 hover:text-indigo-500"
              >Vee-Validate</a
            >
            for forms, and
            <a
              href="https://pwa.nuxtjs.org/"
              target="_blank"
              rel="noopener noreferrer"
              class="text-indigo-600 hover:text-indigo-500"
              >Nuxt/PWA</a
            >.
          </dd>
        </div>

        <div class="relative">
          <dt>
            <div
              class="absolute flex items-center justify-center h-12 w-12 rounded-md bg-indigo-500 text-white"
            >
              <!-- Heroicon name: outline/annotation -->
              <svg
                class="h-6 w-6"
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
                aria-hidden="true"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M7 8h10M7 12h4m1 8l-4-4H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-3l-4 4z"
                />
              </svg>
            </div>
            <p class="ml-16 text-lg leading-6 font-medium text-gray-900">
              Templates
            </p>
          </dt>
          <dd class="mt-2 ml-16 text-base text-gray-500">
            Most coding use-cases covered, including
            <i>auth 'n auth</i> for user-management.
          </dd>
        </div>
      </dl>
    </div>

    <div class="mt-5 sm:mt-8 sm:flex sm:justify-center lg:justify-start">
      <div class="rounded-md shadow">
        <NuxtLink
          to="/get-started"
          class="w-full flex items-center justify-center px-8 py-3 border border-transparent text-base font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 md:py-4 md:text-lg md:px-10"
        >
          Get started</NuxtLink
        >
      </div>
      <div class="mt-3 sm:mt-0 sm:ml-3">
        <a
          href="#"
          class="w-full flex items-center justify-center px-8 py-3 border border-transparent text-base font-medium rounded-md text-indigo-700 bg-indigo-100 hover:bg-indigo-200 md:py-4 md:text-lg md:px-10"
        >
          Live demo
        </a>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { Component, Vue } from "nuxt-property-decorator"

@Component({
  layout: "landing",
})
export default class Landing extends Vue {}
</script>
