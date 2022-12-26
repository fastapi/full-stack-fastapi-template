<template>
    <div>
        <component v-if="props.check"
            :is="CheckCircleIcon" 
            class="text-green-600 flex-shrink-0 -ml-1 mr-3 h-6 w-6" 
            aria-hidden="true" 
        />
        <component v-else
            :is="XCircleIcon" 
            class="text-red-600 flex-shrink-0 -ml-1 mr-3 h-6 w-6" 
            aria-hidden="true" 
        />
    </div>
</template>

<script setup lang="ts">
import { CheckCircleIcon, XCircleIcon } from "@heroicons/vue/24/outline"

const props = defineProps({
    check: Boolean
})
</script>