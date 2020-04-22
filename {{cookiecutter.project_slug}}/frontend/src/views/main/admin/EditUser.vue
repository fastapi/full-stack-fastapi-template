<template>
  <v-container fluid>
    <validation-observer ref="observer" v-slot="{ invalid }">
      <form @submit.prevent="onSubmit" @reset.prevent="onReset">
        <v-card class="ma-3 pa-3">
          <v-card-title primary-title>
            <div class="headline primary--text">Edit User</div>
          </v-card-title>
          <v-card-text>
            <template>
              <div class="my-3">
                <div class="subheading secondary--text text--lighten-2">Username</div>
                <div v-if="user" class="title primary--text text--darken-2">
                  {{ user.email }}
                </div>
                <div v-else class="title primary--text text--darken-2">-----</div>
              </div>
              <!-- full name -->
              <validation-provider
                v-slot="{ errors }"
                name="Full Name"
                rules="required"
              >
                <v-text-field
                  v-model="fullName"
                  label="Full Name"
                  :error-messages="errors[0]"
                  required
                ></v-text-field>
              </validation-provider>

              <!-- email -->
              <validation-provider
                v-slot="{ errors }"
                rules="required|email"
                name="E-mail"
              >
                <v-text-field
                  v-model="email"
                  label="E-mail"
                  type="email"
                  :error-messages="errors[0]"
                  required
                ></v-text-field>
              </validation-provider>

              <!-- is superuser -->
              <div class="subheading secondary--text text--lighten-2">
                User is superuser
                <span v-if="isSuperuser">(currently is a superuser)</span
                ><span v-else>(currently is not a superuser)</span>
              </div>
              <v-checkbox v-model="isSuperuser" label="Is Superuser"></v-checkbox>

              <!-- is active -->
              <div class="subheading secondary--text text--lighten-2">
                User is active <span v-if="isActive">(currently active)</span
                ><span v-else>(currently not active)</span>
              </div>
              <v-checkbox v-model="isActive" label="Is Active"></v-checkbox>
              <v-row align="center">
                <v-col class="flex-shrink-1">
                  <v-checkbox
                    v-model="setPassword"
                    class="mr-2"
                    label="Override Password"
                  ></v-checkbox>
                </v-col>

                <v-col>
                  <!-- password -->
                  <validation-provider
                    v-slot="{ errors }"
                    :debounce="100"
                    name="Password"
                    vid="password1"
                    :rules="{ required: setPassword }"
                  >
                    <v-text-field
                      v-model="password1"
                      type="password"
                      :disabled="!setPassword"
                      label="Password"
                      :error-messages="errors"
                    ></v-text-field>
                  </validation-provider>

                  <!-- password confirmation -->
                  <validation-provider
                    v-slot="{ errors }"
                    :debounce="100"
                    name="Password confirmation"
                    vid="password2"
                    :rules="{
                      required: setPassword,
                      confirmed: setPassword ? 'password1' : false,
                    }"
                  >
                    <v-text-field
                      v-model="password2"
                      type="password"
                      :disabled="!setPassword"
                      label="Confirm Password"
                      :error-messages="errors"
                    ></v-text-field>
                  </validation-provider>
                </v-col>
              </v-row>
            </template>
          </v-card-text>
          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn @click="cancel">Cancel</v-btn>
            <v-btn type="reset">Reset</v-btn>
            <v-btn type="submit" :disabled="invalid">Save</v-btn>
          </v-card-actions>
        </v-card>
      </form>
    </validation-observer>
  </v-container>
</template>

<script lang="ts">
  import { Component, Vue } from "vue-property-decorator";
  import { IUserProfileUpdate } from "@/interfaces";
  import { adminStore } from "@/store";
  import { required, confirmed, email } from "vee-validate/dist/rules";
  import { ValidationProvider, ValidationObserver, extend } from "vee-validate";

  // register validation rules
  extend("required", { ...required, message: "{_field_} can not be empty" });
  extend("confirmed", { ...confirmed, message: "Passwords do not match" });
  extend("email", { ...email, message: "Invalid email address" });

  @Component({
    components: {
      ValidationObserver,
      ValidationProvider,
    },
  })
  export default class EditUser extends Vue {
    $refs!: {
      observer: InstanceType<typeof ValidationObserver>;
    };

    valid = true;
    fullName = "";
    email = "";
    isActive = true;
    isSuperuser = false;
    setPassword = false;
    password1 = "";
    password2 = "";

    async mounted() {
      await adminStore.getUsers();
      this.onReset();
    }

    onReset() {
      this.setPassword = false;
      this.password1 = "";
      this.password2 = "";
      this.$refs.observer.reset();
      if (this.user) {
        this.fullName = this.user.full_name;
        this.email = this.user.email;
        this.isActive = this.user.is_active;
        this.isSuperuser = this.user.is_superuser;
      }
    }

    cancel() {
      this.$router.back();
    }

    async onSubmit() {
      const success = await this.$refs.observer.validate();

      if (!success) {
        return;
      }

      if (!this.user) {
        return;
      }

      const updatedProfile: IUserProfileUpdate = {};
      /* eslint-disable @typescript-eslint/camelcase */
      if (this.fullName) {
        updatedProfile.full_name = this.fullName;
      }
      if (this.email) {
        updatedProfile.email = this.email;
      }
      updatedProfile.is_active = this.isActive;
      updatedProfile.is_superuser = this.isSuperuser;
      /* eslint-enable @typescript-eslint/camelcase */
      if (this.setPassword) {
        updatedProfile.password = this.password1;
      }
      await adminStore.updateUser({
        id: this.user.id,
        user: updatedProfile,
      });
      this.$router.push("/main/admin/users");
    }

    get user() {
      return adminStore.adminOneUser(+this.$router.currentRoute.params.id);
    }
  }
</script>
