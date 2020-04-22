<template>
  <router-view></router-view>
</template>

<script lang="ts">
  import { Component, Vue } from "vue-property-decorator";
  import { mainStore } from "@/store";

  const routeGuardAdmin = async (_to, _from, next) => {
    if (!mainStore.hasAdminAccess) {
      next("/main");
    } else {
      next();
    }
  };

  @Component
  export default class Admin extends Vue {
    public beforeRouteEnter(to, from, next) {
      routeGuardAdmin(to, from, next);
    }

    public beforeRouteUpdate(to, from, next) {
      routeGuardAdmin(to, from, next);
    }
  }
</script>
