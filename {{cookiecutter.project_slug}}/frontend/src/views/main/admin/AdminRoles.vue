<template>
  <div>
    <v-toolbar light>
      <v-toolbar-title>
        Manage Roles
      </v-toolbar-title>
      <v-spacer></v-spacer>
      <v-btn color="primary" to="/main/admin/roles/create">Create Role</v-btn>
    </v-toolbar>
    <v-data-table :headers="headers" :items="roles">
      <template slot="items" slot-scope="props">
        <td>{{ props.item.name }}</td>
        <td>{{ props.item.description }}</td>
        <td class="justify-center layout px-0">
          <v-tooltip top>
            <span>Edit</span>
            <v-btn slot="activator" flat :to="{name: 'main-admin-roles-edit', params: {id: props.item.id}}">
              <v-icon>edit</v-icon>
            </v-btn>
          </v-tooltip>
        </td>
      </template>
    </v-data-table>
  </div>
</template>

<script lang="ts">
import { Component, Vue } from 'vue-property-decorator';
import { Store } from 'vuex';
import { IUserProfile } from '@/interfaces';
import {readAdminRoles, readAdminUsers} from '@/store/admin/getters';
import {dispatchGetRoles, dispatchGetUsers} from '@/store/admin/actions';

@Component
export default class AdminRoles extends Vue {
  public headers = [
    {
      text: 'Name',
      sortable: true,
      value: 'name',
      align: 'left',
    },
    {
      text: 'Description',
      sortable: true,
      value: 'description',
      align: 'left',
    },
    {
      text: 'Actions',
      value: 'id',
      sortable: false,
    },
  ];
  get roles() {
    return readAdminRoles(this.$store);
  }

  public async mounted() {
    await dispatchGetRoles(this.$store);
  }
}
</script>
