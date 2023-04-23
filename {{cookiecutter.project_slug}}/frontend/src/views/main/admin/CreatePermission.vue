<template>
  <v-container fluid>
    <v-card class="ma-3 pa-3">
      <v-card-title primary-title>
        <div class="headline primary--text">Create Permission</div>
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
        <v-btn @click="submit" :disabled="!valid">
              Save
            </v-btn>
      </v-card-actions>
    </v-card>
  </v-container>
</template>

<script lang="ts">
import { Component, Vue } from 'vue-property-decorator';
import {
    IUserProfile,
    IUserProfileUpdate,
    IUserProfileCreate, IPermission,
} from '@/interfaces';
import {dispatchGetUsers, dispatchCreateUser, dispatchGetRoles, dispatchCreatePermission} from '@/store/admin/actions';
import {readAdminPermissions, readAdminRoles} from "@/store/admin/getters";
import {hasOwnProperty} from "jest";

@Component
export default class CreatePermission extends Vue {
  public valid = false;
  public object: string = '';
  public role_id: object = {};
  public permission_read = false
  public permission_write = false
  public permission_delete = false

  get permissions_set() {
      return { "read": this.permission_read, "write": this.permission_write, "delete": this.permission_delete }
  }
  public async mounted() {
    await dispatchGetUsers(this.$store);
    await dispatchGetRoles(this.$store);
    this.reset();
  }

  public reset() {
    this.object = '';
    this.role_id = {};
    this.permission_read = false;
    this.permission_write = false;
    this.permission_delete = false;
    this.$validator.reset();
  }

  public cancel() {
    this.$router.back();
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

  public async submit() {
    if (await this.$validator.validateAll()) {
      const permission: IPermission = {
          permissions: this.permissions_set,
          object: this.object,
          role_id: this.selectedRole[0]

      };
      await dispatchCreatePermission(this.$store, permission);
      this.$router.push('/main/admin/permissions');
    }
  }
}
</script>
