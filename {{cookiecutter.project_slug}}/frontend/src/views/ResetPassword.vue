<template>
  <v-main>
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
                    >
                    </v-text-field>
                  </validation-provider>
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
                    >
                    </v-text-field>
                  </validation-provider>
                </v-card-text>
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
  </v-main>
</template>

<script lang="ts">
import { Component, Vue } from "vue-property-decorator";
import { appName } from "@/env";
import { commitAddNotification } from "@/store/main/mutations";
import { dispatchResetPassword } from "@/store/main/actions";
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

  public appName = appName;
  public valid = true;
  public password1 = "";
  public password2 = "";

  public mounted() {
    this.checkToken();
  }

  public onReset() {
    this.password1 = "";
    this.password2 = "";
    this.$refs.observer.reset();
  }

  public cancel() {
    this.$router.push("/");
  }

  public checkToken() {
    const token = this.$router.currentRoute.query.token as string;
    if (!token) {
      commitAddNotification(this.$store, {
        content: "No token provided in the URL, start a new password recovery",
        color: "error",
      });
      this.$router.push("/recover-password");
    } else {
      return token;
    }
  }

  public async onSubmit() {
    const success = await this.$refs.observer.validate();
    if (!success) {
      return;
    }

    const token = this.checkToken();
    if (token) {
      await dispatchResetPassword(this.$store, { token, password: this.password1 });
      this.$router.push("/");
    }
  }
}
</script>
