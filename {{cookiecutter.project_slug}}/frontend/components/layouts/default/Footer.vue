<template>
    <footer class="mt-24 bg-gray-900 sm:mt-12">
      <div class="mx-auto max-w-md overflow-hidden py-12 px-4 sm:max-w-3xl sm:px-6 lg:max-w-7xl lg:px-8">
        <nav class="-mx-5 -my-2 flex flex-wrap justify-center" aria-label="Footer">
          <div v-for="item in footerNavigation.main" :key="item.name" class="px-5 py-2">
            <NuxtLink :to="item.to" class="text-base text-gray-400 hover:text-gray-300">{{ item.name }}</NuxtLink>
          </div>
        </nav>
        <div class="mt-8 flex justify-center space-x-6">
          <a v-for="item in footerNavigation.social" :key="item.name" :href="item.href" class="text-gray-400 hover:text-gray-300">
            <span class="sr-only">{{ item.name }}</span>
            <component :is="item.icon" class="h-6 w-6" aria-hidden="true" />
          </a>
        </div>
        <p class="mt-8 text-center text-base text-gray-400">&copy; 2022 {{ siteName }}. All rights reserved.</p>
      </div>
    </footer>
</template>

<script setup lang="ts">
import { defineComponent, h } from "vue"

const siteName: String = "Your Company, Inc"

const footerNavigation = {
  main: [
    { name: "About", to: "/about" },
    { name: "Blog", to: "/blog" },
  ],
  social: [
    {
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
    },
  ],
}
</script>