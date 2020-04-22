<template>
  <v-content>
    <v-container fluid class="fill-height">
      <v-row align="center" justify="center">
        <v-col cols="12" sm="8" md="4">
          <validation-observer ref="observer" v-slot="{ invalid }">
            <form @submit.prevent="onSubmit" @reset.prevent="onReset">
              <v-card class="elevation-12">
                <v-toolbar dark color="primary">
                  <v-toolbar-title>{{ appName }} - Reset Password</v-toolbar-title>
                </v-toolbar>
                <v-card-text>
                  <p class="subheading">Enter your new password below</p>
                </v-card-text>

                <!-- password -->
                <validation-provider
                  v-slot="{ errors }"
                  :debounce="100"
                  name="Password"
                  vid="password1"
                  rules="required"
                >
                  <v-text-field
                    v-model="password1"
                    type="password"
                    label="Password"
                    :error-messages="errors"
                  ></v-text-field>
                </validation-provider>

                <!-- password confirmation -->
                <validation-provider
                  v-slot="{ errors }"
                  debounce="100"
                  name="Password confirmation"
                  vid="password2"
                  rules="required|confirmed:password1"
                >
                  <v-text-field
                    v-model="password2"
                    type="password"
                    label="Confirm Password"
                    :error-messages="errors"
                  ></v-text-field>
                </validation-provider>

                <v-card-actions>
                  <v-spacer></v-spacer>
                  <v-btn @click="cancel">Cancel</v-btn>
                  <v-btn type="reset">Clear</v-btn>
                  <v-btn type="submit" :disabled="invalid">Save</v-btn>
                </v-card-actions>
              </v-card>
            </form>
          </validation-observer>
        </v-col>
      </v-row>
    </v-container>
  </v-content>
</template>

<script lang="ts">
  import { Component, Vue } from "vue-property-decorator";
  import { appName } from "@/env";
  import { mainStore } from "@/store";
  import { required, confirmed } from "vee-validate/dist/rules";
  import { ValidationProvider, ValidationObserver, extend } from "vee-validate";

  // register validation rules
  extend("required", { ...required, message: "{_field_} can not be empty" });
  extend("confirmed", { ...confirmed, message: "Passwords do not match" });

  @Component({
    components: {
      ValidationObserver,
      ValidationProvider,
    },
  })
  export default class UserProfileEdit extends Vue {
    $refs!: {
      observer: InstanceType<typeof ValidationObserver>;
    };

    appName = appName;
    valid = true;
    password1 = "";
    password2 = "";

    mounted() {
      this.checkToken();
    }

    onReset() {
      this.password1 = "";
      this.password2 = "";
      this.$refs.observer.reset();
    }

    cancel() {
      this.$router.push("/");
    }

    checkToken() {
      const token = this.$router.currentRoute.query.token as string;
      if (!token) {
        mainStore.addNotification({
          content: "No token provided in the URL, start a new password recovery",
          color: "error",
        });
        this.$router.push("/recover-password");
      } else {
        return token;
      }
    }

    async onSubmit() {
      const success = await this.$refs.observer.validate();

      if (!success) {
        return;
      }

      const token = this.checkToken();

      if (token) {
        await mainStore.resetPassword({ token, password: this.password1 });
        this.$router.push("/");
      }
    }
  }
</script>
