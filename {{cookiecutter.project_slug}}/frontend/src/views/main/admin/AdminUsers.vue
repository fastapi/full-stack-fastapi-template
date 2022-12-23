<template>
  <div>
    <v-toolbar light>
      <v-toolbar-title> Manage Users </v-toolbar-title>
      <v-spacer></v-spacer>
      <v-btn color="primary" to="/main/admin/users/create">Create User</v-btn>
    </v-toolbar>
    <v-data-table :headers="headers" :items="users">
      <!-- eslint-disable-next-line vue/valid-v-slot -->
      <template #item.is_active="{ item }">
        <v-icon v-if="item.is_active">mdi-check</v-icon>
      </template>
      <!-- eslint-disable-next-line vue/valid-v-slot -->
      <template #item.is_superuser="{ item }">
        <v-icon v-if="item.is_superuser">mdi-check</v-icon>
      </template>
      <!-- eslint-disable-next-line vue/valid-v-slot -->
      <template #item.actions="{ item }">
        <v-btn
          slot="activator"
          icon
          :to="{ name: 'main-admin-users-edit', params: { id: item.id } }"
        >
          <v-icon>mdi-pencil</v-icon>
        </v-btn>
      </template>
    </v-data-table>
  </div>
</template>

<script lang="ts">
import { Component, Vue } from "vue-property-decorator";
import { readAdminUsers } from "@/store/admin/getters";
import { dispatchGetUsers } from "@/store/admin/actions";

@Component
export default class AdminUsers extends Vue {
  public headers = [
    {
      text: "Name",
      sortable: true,
      value: "full_name",
      align: "left",
    },
    {
      text: "Email",
      sortable: true,
      value: "email",
      align: "left",
    },
    {
      text: "Full Name",
      sortable: true,
      value: "full_name",
      align: "left",
    },
    {
      text: "Is Active",
      sortable: true,
      value: "is_active",
      align: "left",
    },
    {
      text: "Is Superuser",
      sortable: true,
      value: "is_superuser",
      align: "left",
    },
    {
      text: "Actions",
      value: "actions",
      sortable: false,
    },
  ];
  get users() {
    return readAdminUsers(this.$store);
  }

  public async mounted() {
    await dispatchGetUsers(this.$store);
  }
}
</script>
