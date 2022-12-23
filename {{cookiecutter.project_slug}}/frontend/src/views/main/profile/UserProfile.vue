<template>
  <v-container fluid>
    <v-card class="ma-3 pa-3">
      <v-card-title primary-title>
        <div class="headline primary--text">User Profile</div>
      </v-card-title>
      <v-card-text>
        <div class="my-4">
          <div class="subheading secondary--text text--lighten-3">Full Name</div>
          <div
            v-if="userProfile && userProfile.full_name"
            class="title primary--text text--darken-2"
          >
            {{ userProfile.full_name }}
          </div>
          <div v-else class="title primary--text text--darken-2">-----</div>
        </div>
        <div class="my-3">
          <div class="subheading secondary--text text--lighten-3">Email</div>
          <div
            v-if="userProfile && userProfile.email"
            class="title primary--text text--darken-2"
          >
            {{ userProfile.email }}
          </div>
          <div v-else class="title primary--text text--darken-2">-----</div>
        </div>
      </v-card-text>
      <v-card-actions>
        <v-btn to="/main/profile/edit">Edit</v-btn>
        <v-btn to="/main/profile/password">Change password</v-btn>
      </v-card-actions>
    </v-card>
  </v-container>
</template>

<script lang="ts">
import { Component, Vue } from "vue-property-decorator";
import { readUserProfile } from "@/store/main/getters";

@Component
export default class UserProfile extends Vue {
  get userProfile() {
    return readUserProfile(this.$store);
  }

  public goToEdit() {
    this.$router.push("/main/profile/edit");
  }

  public goToPassword() {
    this.$router.push("/main/profile/password");
  }
}
</script>
