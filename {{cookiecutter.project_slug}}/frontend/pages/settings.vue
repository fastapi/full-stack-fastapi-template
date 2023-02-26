<template>
  <main class="flex min-h-full mx-auto max-w-7xl px-2 sm:px-6 lg:px-8">
    <div class="p-5">
      <div class="lg:grid lg:grid-cols-12 lg:gap-x-5">
        <aside class="py-6 px-2 sm:px-6 lg:col-span-3 lg:py-0 lg:px-0">
          <nav class="space-y-1" aria-label="tabs">
            <button v-for="item in navigation" :key="`settings-${item.id}`"
              :class="[item.id === selected
                ? 'text-ochre-700 hover:text-ochre-700'
                : 'text-gray-900 hover:text-gray-900', 'group rounded-md px-3 py-2 flex items-center text-sm font-medium']" @click.prevent="changeSelection(item.id)">
              <component :is="item.icon" :class="[item.id === selected
                ? 'text-ochre-700 group-hover:text-ochre-700'
                : 'text-gray-400 group-hover:text-gray-500', 'flex-shrink-0 -ml-1 mr-3 h-6 w-6']" aria-hidden="true" />
              <span class="truncate">{{ item.name }}</span>
            </button>
            <button v-if="auth.is_superuser"
              class="text-gray-900 hover:text-gray-900 group rounded-md px-3 py-2 flex items-center text-sm font-medium cursor-pointer"
              @click.prevent="navigateTo('/moderation')">
              <component :is="UsersIcon" class="text-gray-400 group-hover:text-gray-500 flex-shrink-0 -ml-1 mr-3 h-6 w-6"
                aria-hidden="true" />
              <span class="truncate">Moderation</span>
            </button>
          </nav>
        </aside>
        <div class="space-y-6 ml-3 sm:px-6 lg:col-span-9 min-w-full lg:px-0">
          <div v-if="selected === 'ACCOUNT'">
            <SettingsProfile />
          </div>
          <div v-if="selected === 'SECURITY'">
            <SettingsSecurity />
          </div>
        </div>
      </div>
    </div>
  </main>
</template>

<script setup lang="ts">
import { KeyIcon, UserCircleIcon, UsersIcon } from "@heroicons/vue/24/outline"
import { useAuthStore } from "@/stores"

definePageMeta({
  middleware: ["authenticated"],
});

const auth = useAuthStore()

const navigation = [
  { name: "Account", id: "ACCOUNT", icon: UserCircleIcon },
  { name: "Security", id: "SECURITY", icon: KeyIcon },
]
const title = "Settings"
const description = "Update your personal settings, or delete your account."
const selected = ref("ACCOUNT")

function changeSelection(selection: string) {
  selected.value = selection
}
</script>