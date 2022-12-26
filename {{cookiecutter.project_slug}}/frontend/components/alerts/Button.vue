<template>
    <button 
        type="button" 
        class="rounded-full bg-white p-1 text-gray-400 hover:text-gray-500 focus:outline-none focus:ring-2 focus:ring-rose-500 focus:ring-offset-2"
    >
        <span class="sr-only">View notifications</span>
        <BellIcon class="h-6 w-6" aria-hidden="true" />
    </button>
</template>

  
<script setup>
  import { BellIcon } from "@heroicons/vue/24/outline"
</script>