<template>
  <button
    type="submit"
    class="text-gray-900 hover:text-gray-900 group rounded-md px-3 py-2 flex items-center text-sm font-medium"
    @click.prevent="submit"
  >
    <component 
      :is="AtSymbolIcon" 
      class="text-gray-400 group-hover:text-gray-500 flex-shrink-0 -ml-1 mr-3 h-6 w-6" 
      aria-hidden="true" 
    />
    <span class="truncate">Validate email</span>
  </button>
</template>
  
<script setup lang="ts">
import { AtSymbolIcon } from "@heroicons/vue/24/outline"
import { useAuthStore } from "@/stores"

const auth = useAuthStore()

async function submit() {
  await auth.sendEmailValidation()
}
</script>