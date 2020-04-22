<template>
  <div>
    <v-navigation-drawer
      v-model="showDrawer"
      persistent
      :mini-variant="miniDrawer"
      fixed
      dark
      app
    >
      <v-list>
        <v-subheader>Main menu</v-subheader>
        <v-list-item to="/main/dashboard">
          <v-list-item-action>
            <v-icon>mdi-web</v-icon>
          </v-list-item-action>
          <v-list-item-content>
            <v-list-item-title>Dashboard</v-list-item-title>
          </v-list-item-content>
        </v-list-item>
        <v-list-item to="/main/profile/view">
          <v-list-item-action>
            <v-icon>mdi-account</v-icon>
          </v-list-item-action>
          <v-list-item-content>
            <v-list-item-title>Profile</v-list-item-title>
          </v-list-item-content>
        </v-list-item>
        <v-list-item to="/main/profile/edit">
          <v-list-item-action>
            <v-icon>mdi-pencil</v-icon>
          </v-list-item-action>
          <v-list-item-content>
            <v-list-item-title>Edit Profile</v-list-item-title>
          </v-list-item-content>
        </v-list-item>
        <v-list-item to="/main/profile/password">
          <v-list-item-action>
            <v-icon>mdi-key</v-icon>
          </v-list-item-action>
          <v-list-item-content>
            <v-list-item-title>Change Password</v-list-item-title>
          </v-list-item-content>
        </v-list-item>
      </v-list>
      <v-divider></v-divider>
      <v-list v-show="hasAdminAccess" subheader>
        <v-subheader>Admin</v-subheader>
        <v-list-item to="/main/admin/users/all">
          <v-list-item-action>
            <v-icon>mdi-account-multiple</v-icon>
          </v-list-item-action>
          <v-list-item-content>
            <v-list-item-title>Manage Users</v-list-item-title>
          </v-list-item-content>
        </v-list-item>
        <v-list-item to="/main/admin/users/create">
          <v-list-item-action>
            <v-icon>mdi-account-plus</v-icon>
          </v-list-item-action>
          <v-list-item-content>
            <v-list-item-title>Create User</v-list-item-title>
          </v-list-item-content>
        </v-list-item>
      </v-list>

      <template v-slot:append>
        <v-list>
          <v-list-item @click="logout">
            <v-list-item-action>
              <v-icon>mdi-close</v-icon>
            </v-list-item-action>
            <v-list-item-content>
              <v-list-item-title>Logout</v-list-item-title>
            </v-list-item-content>
          </v-list-item>

          <v-divider></v-divider>

          <v-list-item @click="switchMiniDrawer">
            <v-list-item-action>
              <v-icon>
                {{ miniDrawer ? "mdi-chevron-right" : "mdi-chevron-left" }}
              </v-icon>
            </v-list-item-action>
            <v-list-item-content>
              <v-list-item-title>Collapse</v-list-item-title>
            </v-list-item-content>
          </v-list-item>
        </v-list>
      </template>
    </v-navigation-drawer>

    <v-app-bar dark color="primary" app>
      <v-app-bar-nav-icon @click.stop="switchShowDrawer"></v-app-bar-nav-icon>
      <v-toolbar-title v-text="appName"></v-toolbar-title>

      <v-spacer></v-spacer>

      <v-menu bottom left offset-y>
        <template v-slot:activator="{ on }">
          <v-btn icon v-on="on">
            <v-icon>mdi-dots-vertical</v-icon>
          </v-btn>
        </template>
        <v-list>
          <v-list-item to="/main/profile">
            <v-list-item-content>
              <v-list-item-title>Profile</v-list-item-title>
            </v-list-item-content>
            <v-list-item-action>
              <v-icon>mdi-account</v-icon>
            </v-list-item-action>
          </v-list-item>
          <v-list-item @click="logout">
            <v-list-item-content>
              <v-list-item-title>Logout</v-list-item-title>
            </v-list-item-content>
            <v-list-item-action>
              <v-icon>mdi-close</v-icon>
            </v-list-item-action>
          </v-list-item>
        </v-list>
      </v-menu>
    </v-app-bar>
    <v-content>
      <router-view></router-view>
    </v-content>
    <v-footer class="pa-3" fixed app>
      <v-spacer></v-spacer>
      <span>&copy; {{ appName }}</span>
    </v-footer>
  </div>
</template>

<script lang="ts">
  import { Vue, Component } from "vue-property-decorator";

  import { appName } from "@/env";
  import { mainStore } from "@/store";

  const routeGuardMain = async (to, _from, next) => {
    if (to.path === "/main") {
      next("/main/dashboard");
    } else {
      next();
    }
  };

  @Component
  export default class Main extends Vue {
    public appName = appName;

    public beforeRouteEnter(to, from, next) {
      routeGuardMain(to, from, next);
    }

    public beforeRouteUpdate(to, from, next) {
      routeGuardMain(to, from, next);
    }

    get miniDrawer() {
      return mainStore.dashboardMiniDrawer;
    }

    get showDrawer() {
      return mainStore.dashboardShowDrawer;
    }

    set showDrawer(value) {
      mainStore.setDashboardShowDrawer(value);
    }

    public switchShowDrawer() {
      mainStore.setDashboardShowDrawer(!mainStore.dashboardShowDrawer);
    }

    public switchMiniDrawer() {
      mainStore.setDashboardMiniDrawer(!mainStore.dashboardMiniDrawer);
    }

    public get hasAdminAccess() {
      return mainStore.hasAdminAccess;
    }

    public async logout() {
      await mainStore.userLogOut();
    }
  }
</script>
