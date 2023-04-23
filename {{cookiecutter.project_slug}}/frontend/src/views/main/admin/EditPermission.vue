<template>
  <v-container fluid>
    <v-card class="ma-3 pa-3">
      <v-card-title primary-title>
        <div class="headline primary--text">Edit Permission</div>
      </v-card-title>
      <v-card-text>
        <template>
          <v-form v-model="valid" ref="form" lazy-validation>
            <v-text-field label="Object" v-model="object" required></v-text-field>
              <v-select
                required
                v-model="role_id"
                :items="roles"
                item-text="text"
                item-value="value"
                label="Select"
                return-object
                single-line
              ></v-select>

              <v-checkbox
                 v-model="permission_read"
                 label="Allow read"
                 hide-details
              ></v-checkbox>
              <v-checkbox
                 v-model="permission_write"
                 label="Allow write"
                 hide-details
              ></v-checkbox>
              <v-checkbox
                 v-model="permission_delete"
                 label="Allow delete"
                 hide-details
              ></v-checkbox>
          </v-form>
        </template>
      </v-card-text>
      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn @click="cancel">Cancel</v-btn>
        <v-btn @click="reset">Reset</v-btn>
        <v-btn
          @click="submit"
          :disabled="!valid"
        >
          Save
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-container>
</template>

<script lang="ts">
import { Component, Vue } from 'vue-property-decorator';
import { IPermissionUpdate, IPermission } from '@/interfaces';
import {
    dispatchGetPermissions,
    dispatchGetRoles,
    dispatchGetUsers,
    dispatchUpdatePermission,
    dispatchUpdateUser
} from '@/store/admin/actions';
import {readAdminOnePermission, readAdminOneRole, readAdminOneUser, readAdminRoles} from '@/store/admin/getters';

@Component
export default class EditPermission extends Vue {
  public valid = false;
  public object: string = '';
  public role_id: object = {};
  public permission_read = false
  public permission_write = false
  public permission_delete = false

  public async mounted() {
      await dispatchGetRoles(this.$store)
      await dispatchGetPermissions(this.$store)
      this.reset();
  }

  get permissions_set() {
      return { "read": this.permission_read, "write": this.permission_write, "delete": this.permission_delete }
  }

  get roleList() {
      return readAdminRoles(this.$store)
  }

  get roles() {
      return Object.keys(this.roleList).map((key) => ({text:this.roleList[key].name, value:this.roleList[key].id}));
  }

  get selectedRole() {
      if (this.role_id.hasOwnProperty('value')) {
          return this.roleList.filter( r => r.id === this.role_id['value'])
      }
      return {}
  }

  public reset() {
    this.$validator.reset();
    if (this.permission) {
        this.object = this.permission.object;
        this.role_id = this.roles.filter( r => r.value === this.permission?.['role'].id)[0]
        this.permission_read = this.permission.permissions?.['read'] === '1' ? true : false;
        this.permission_write = this.permission.permissions?.['write'] === '1' ? true : false;
        this.permission_delete = this.permission.permissions?.['delete'] === '1' ? true : false;
        console.log("PREAD:", this.permission.permissions?.['read'] === '1')
    }
  }

  public cancel() {
    this.$router.back();
  }

  public async submit() {
    if (await this.$validator.validateAll()) {
      const updatedPermission: IPermissionUpdate = {};
      updatedPermission.id = this.permission?.id
      updatedPermission.object = this.object
      updatedPermission.role_id = this.selectedRole[0]
      updatedPermission.permissions = this.permissions_set
      if(this.permission!.id) {
          await dispatchUpdatePermission(this.$store, {id: this.permission!.id, permission: updatedPermission});
      }
      this.$router.push('/main/admin/permissions');
    }
  }

  get permission() {
    return readAdminOnePermission(this.$store)(+this.$router.currentRoute.params.id);
  }
}
</script>
