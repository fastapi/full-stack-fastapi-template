<template>
  <v-container fluid>
    <v-card class="ma-3 pa-3">
      <v-card-title primary-title>
        <div class="headline primary--text">Edit Role</div>
      </v-card-title>
      <v-card-text>
        <template>
          <div class="my-3">
<!--            <div class="subheading secondary&#45;&#45;text text&#45;&#45;lighten-2">Username</div>-->
            <div
              class="title primary--text text--darken-2"
              v-if="role"
            >{{role.name}}</div>
          </div>
          <v-form
            v-model="valid"
            ref="form"
            lazy-validation
          >
            <v-text-field
              label="Name"
              v-model="name"
              required
            ></v-text-field>
            <v-text-field
              label="Role description"
              v-model="description"
            ></v-text-field>
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
import {IRoleUpdate, IUserProfile, IUserProfileUpdate} from '@/interfaces';
import {dispatchGetUsers, dispatchUpdateRole, dispatchUpdateUser} from '@/store/admin/actions';
import {readAdminOneRole, readAdminOneUser} from '@/store/admin/getters';

@Component
export default class EditUser extends Vue {
  public valid = true;
  public name: string = '';
  public description: string = '';

  public async mounted() {
    await dispatchGetUsers(this.$store);
    this.reset();
  }

  public reset() {
    this.$validator.reset();
    if (this.role) {
      this.name = this.role.name;
      this.description = this.role.description || '';
    }
  }

  public cancel() {
    this.$router.back();
  }

  public async submit() {
    if (await this.$validator.validateAll()) {
      const updatedRole: IRoleUpdate = {};
      if (this.name) {
        updatedRole.name = this.name;
        updatedRole.description = this.description;
      }
      await dispatchUpdateRole(this.$store, { id: this.role!.id, role: updatedRole });
      this.$router.push('/main/admin/roles');
    }
  }

  get role() {
    return readAdminOneRole(this.$store)(+this.$router.currentRoute.params.id);
  }
}
</script>
