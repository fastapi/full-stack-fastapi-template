<template>
  <div>
    <v-snackbar v-model="show" :color="currentNotificationColor">
      <v-progress-circular
        v-show="showProgress"
        class="ma-2"
        indeterminate
      ></v-progress-circular
      >{{ currentNotificationContent }}
      <v-btn text @click.native="close">Close</v-btn>
    </v-snackbar>
  </div>
</template>
<script lang="ts">
  import { Vue, Component, Watch } from "vue-property-decorator";
  import { IAppNotification } from "@/interfaces";
  import { mainStore } from "@/store";

  @Component
  export default class NotificationsManager extends Vue {
    public show = false;
    public text = "";
    public showProgress = false;
    public currentNotification: IAppNotification | false = false;

    public async hide() {
      this.show = false;
      await new Promise((resolve, _reject) => setTimeout(() => resolve(), 500));
    }

    public async close() {
      await this.hide();
      await this.removeCurrentNotification();
    }

    public async removeCurrentNotification() {
      if (this.currentNotification) {
        mainStore.removeNotification(this.currentNotification);
      }
    }

    public get firstNotification() {
      return mainStore.firstNotification;
    }

    public async setNotification(notification: IAppNotification | false) {
      if (this.show) {
        await this.hide();
      }
      if (notification) {
        this.currentNotification = notification;
        this.showProgress = notification.showProgress || false;
        this.show = true;
      } else {
        this.currentNotification = false;
      }
    }

    @Watch("firstNotification")
    public async onNotificationChange(newNotification: IAppNotification | false) {
      if (newNotification !== this.currentNotification) {
        await this.setNotification(newNotification);
        if (newNotification) {
          mainStore.removeNotificationDelayed({
            notification: newNotification,
            timeout: 6500,
          });
        }
      }
    }

    public get currentNotificationContent() {
      return (this.currentNotification && this.currentNotification.content) || "";
    }

    public get currentNotificationColor() {
      return (this.currentNotification && this.currentNotification.color) || "info";
    }
  }
</script>
