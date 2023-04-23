<template>
  <div>
    <v-toolbar light>
      <v-toolbar-title>
        Manage Permissions
      </v-toolbar-title>
      <v-spacer></v-spacer>
      <v-btn color="primary" to="/main/admin/permissions/create">Create Permission</v-btn>
    </v-toolbar>
    <v-data-table :headers="headers" :items="permissions">
      <template slot="items" slot-scope="props">
        <td>{{ props.item.object }}</td>
        <td>{{ props.item.role.name }}</td>
        <td class="justify-center layout px-0">
          <v-tooltip top>
            <span>Edit</span>
            <v-btn slot="activator" flat :to="{name: 'main-admin-permissions-edit', params: {id: props.item.id}}">
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
import {readAdminPermissions, readAdminUsers} from '@/store/admin/getters';
import {dispatchGetPermissions, dispatchGetUsers} from '@/store/admin/actions';

@Component
export default class AdminPermissions extends Vue {
  public headers = [
    {
      text: 'Object',
      sortable: true,
      value: 'object',
      align: 'left',
    },
    {
      text: 'Role',
      value: 'role.name',
      align: 'left',
    },
    {
      text: 'Actions',
      value: 'id',
    },
  ];
  get permissions() {
    return readAdminPermissions(this.$store);
  }

  public async mounted() {
    await dispatchGetPermissions(this.$store);
  }
}
</script>
