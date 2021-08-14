<template>
  <div class="flex justify-center max-w-7xl mx-auto py-3 px-3 sm:px-6 lg:px-8">
    <div
      v-show="showNotification"
      :class="`animate-fade-${fadeState} bg-${currentNotificationColor}-100 p-5 w-full sm:w-1/2 rounded object-center`"
    >
      <div class="flex justify-between">
        <div class="flex space-x-3">
          <!-- Heroicon name: outline/information-circle -->
          <svg
            v-if="!showProgress"
            :class="`flex-none text-${currentNotificationColor}-500 h-6 w-6`"
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            aria-hidden="true"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
          <svg
            v-else
            :class="`animate-spin flex-none text-${currentNotificationColor}-500 h-6 w-6`"
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            aria-hidden="true"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"
            />
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
            />
          </svg>
          <div
            :class="`flex-1 leading-tight text-sm text-${currentNotificationColor}-700 font-medium`"
          >
            {{ currentNotificationContent }}
          </div>
        </div>
        <svg
          xmlns="http://www.w3.org/2000/svg"
          viewBox="0 0 24 24"
          :class="`flex-none fill-current text-${currentNotificationColor}-600 h-6 w-6`"
          @click.prevent="close"
        >
          <path
            d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"
          />
        </svg>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import {
  Action,
  Component,
  Mutation,
  Getter,
  Watch,
  Vue,
} from "nuxt-property-decorator"
import { AppNotification } from "@/store/main/state"

@Component
export default class RecoverPassword extends Vue {
  @Getter("main/firstNotification") firstNotification
  @Mutation("main/removeNotification") mutateNotification
  @Action("main/removeNotification") removeNotification
  public showNotification: boolean = false
  public fadeState: string = "in"
  public showProgress: boolean = false
  public currentNotification: AppNotification | false = false

  public async hide() {
    this.fadeState = "out"
    this.showNotification = false
    await new Promise<void>((resolve) => setTimeout(() => resolve(), 500))
  }

  public async close() {
    this.hide()
    if (this.currentNotification) {
      await this.mutateNotification(this.currentNotification)
    }
  }

  public setNotification(notification: AppNotification | false) {
    if (notification) {
      this.currentNotification = notification
      this.showProgress = notification.showProgress || false
      this.fadeState = "in"
      this.showNotification = true
    } else {
      this.currentNotification = false
    }
  }

  @Watch("firstNotification", { immediate: true })
  public async onNotificationChange(newNotification: AppNotification | false) {
    if (newNotification !== this.currentNotification) {
      this.setNotification(newNotification)
      if (newNotification) {
        await this.removeNotification({
          notification: newNotification,
          timeout: 2000,
        })
      }
    }
    if (!this.currentNotification) {
      this.hide()
    }
  }

  public get currentNotificationContent() {
    return (this.currentNotification && this.currentNotification.content) || ""
  }

  public get currentNotificationColor() {
    const colormatch = {
      info: "blue",
      error: "red",
      success: "green",
    }
    return colormatch[
      (this.currentNotification && this.currentNotification.color) || "info"
    ]
  }
}
</script>
