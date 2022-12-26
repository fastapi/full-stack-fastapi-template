import { INotification } from "@/interfaces"
import { generateUUID } from "@/utilities"

export const useToastStore = defineStore("toasts", {
  state: () => ({
    notifications: [] as INotification[]
  }),
  getters: {
    first: (state) => state.notifications.length > 0 && state.notifications[0],
    notices: (state) => state.notifications
  },
  actions: {
    addNotice (payload: INotification) {
      payload.uid = generateUUID()
      if (!payload.icon) payload.icon = "success"
      this.notices.push(payload)
    },
    removeNotice (payload: INotification) {
      this.notifications = this.notices.filter(
        (note) => note !== payload
      )
    },
    async timeoutNotice (payload: INotification, timeout: number = 2000) {
      await new Promise((resolve) => {
        setTimeout(() => {
          this.removeNotice(payload)
          resolve(true)
        }, timeout)
      })
    },
    // reset state using `$reset`
    deleteNotices() {
      this.$reset()
    }
  }
})