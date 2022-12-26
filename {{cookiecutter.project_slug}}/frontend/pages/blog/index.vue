<template>
    <main class="max-w-none mx-auto sm:w-3/5 bg-white px-4 pt-10 pb-20 sm:px-6">
      <div class="relative mx-auto max-w-lg divide-y-2 divide-gray-200 lg:max-w-7xl">
        <div>
          <h2 class="text-3xl font-bold tracking-tight text-gray-900 sm:text-4xl">{{ title }}</h2>
          <p class="mt-3 text-xl text-gray-500 sm:mt-4">{{ description }}</p>
        </div>
        <div class="mt-8 grid gap-16 pt-10 lg:grid-cols-3 lg:gap-x-5 lg:gap-y-12">
          <div v-for="blog in blogPosts" :key="blog.id">
            <div class="space-x-2">
              <span v-for="c in blog.categories.split(',')" 
                :key="`category-${c.trim()}`" 
                class="inline-flex items-center px-3 py-0.5 rounded-full text-sm font-medium bg-gray-100 text-gray-800"
              >{{ c.trim() }}</span>
            </div>
            <NuxtLink :to="blog._path" class="mt-4 block">
              <p class="text-xl font-semibold text-gray-900">{{ blog.title }}</p>
              <p class="mt-3 text-base text-gray-500">{{ blog.description }}</p>
            </NuxtLink>
            <div class="mt-4 flex items-center">
              <div>
                <p class="text-sm font-medium text-gray-900">
                  {{ blog.author }}
                </p>
                <div class="flex space-x-1 text-sm text-gray-500">
                  <time :datetime="blog.publishedAt">{{ readableDate(blog.publishedAt) }}</time>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>
</template>

<script setup lang="ts">
import { readableDate } from "@/utilities"

definePageMeta({
  middleware: ["refresh"],
});

const title = "Recent blog posts"
const description = "Thoughts from the world of me."
const { data: blogPosts } = await useAsyncData("in", () => {
  return queryContent("/blog").find()
})
</script>