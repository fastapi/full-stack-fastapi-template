<template>
  <v-main>
    <v-container fluid fill-height>
      <v-row align="center" justify="center">
        <v-col cols="12" sm="8" md="6" l="5" xl="4">
          <v-card class="elevation-12">
            <v-toolbar dark color="primary">
              <v-toolbar-title>{{ appName }}</v-toolbar-title>
              <v-spacer></v-spacer>
            </v-toolbar>
            <v-card-text>
              <v-form @keyup.enter="submit">
                <v-text-field
                  v-model="email"
                  prepend-icon="mdi-account"
                  name="login"
                  label="Login"
                  type="text"
                  @keyup.enter="submit"
                ></v-text-field>
                <v-text-field
                  id="password"
                  v-model="password"
                  prepend-icon="mdi-lock"
                  name="password"
                  label="Password"
                  type="password"
                  @keyup.enter="submit"
                ></v-text-field>
              </v-form>
              <div v-if="loginError">
                <v-alert :value="loginError" transition="fade-transition" type="error">
                  Incorrect email or password
                </v-alert>
              </div>
              <v-col class="caption text-xs-right"
                ><router-link to="/recover-password"
                  >Forgot your password?</router-link
                ></v-col
              >
            </v-card-text>
            <v-card-actions>
              <v-spacer></v-spacer>
              <v-btn @click.prevent="submit">Login</v-btn>
            </v-card-actions>
          </v-card>
        </v-col>
      </v-row>
    </v-container>
  </v-main>
</template>

<script lang="ts">
import { Component, Vue } from "vue-property-decorator";
import { appName } from "@/env";
import { readLoginError } from "@/store/main/getters";
import { dispatchLogIn } from "@/store/main/actions";

@Component
export default class Login extends Vue {
  public email = "";
  public password = "";
  public appName = appName;

  public get loginError() {
    return readLoginError(this.$store);
  }

  public submit() {
    dispatchLogIn(this.$store, { username: this.email, password: this.password });
  }
}
</script>

<style></style>
