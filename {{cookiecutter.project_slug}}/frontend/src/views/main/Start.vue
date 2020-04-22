<template>
  <router-view></router-view>
</template>

<script lang="ts">
  import { Component, Vue } from "vue-property-decorator";
  import { mainStore } from "@/store";

  const startRouteGuard = async (to, _from, next) => {
    await mainStore.checkLoggedIn();
    if (mainStore.isLoggedIn) {
      if (to.path === "/login" || to.path === "/") {
        next("/main");
      } else {
        next();
      }
    } else if (mainStore.isLoggedIn === false) {
      if (to.path === "/" || (to.path as string).startsWith("/main")) {
        next("/login");
      } else {
        next();
      }
    }
  };

  @Component
  export default class Start extends Vue {
    public beforeRouteEnter(to, from, next) {
      startRouteGuard(to, from, next);
    }

    public beforeRouteUpdate(to, from, next) {
      startRouteGuard(to, from, next);
    }
  }
</script>
