<template>
  <v-container fluid>
    <validation-observer ref="observer" v-slot="{ invalid }">
      <form @submit.prevent="onSubmit" @reset.prevent="onReset">
        <v-card class="ma-3 pa-3">
          <v-card-title primary-title>
            <div class="headline primary--text">Set Password</div>
          </v-card-title>
          <v-card-text>
            <div class="my-3">
              <div class="subheading secondary--text text--lighten-2">User</div>
              <div
                v-if="userProfile.full_name"
                class="title primary--text text--darken-2"
              >
                {{ userProfile.full_name }}
              </div>
              <div v-else class="title primary--text text--darken-2">
                {{ userProfile.email }}
              </div>
            </div>
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
              :debounce="100"
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
import { readUserProfile } from "@/store/main/getters";
import { dispatchUpdateUserProfile } from "@/store/main/actions";
import { ValidationProvider, ValidationObserver, extend } from "vee-validate";
import { required, confirmed } from "vee-validate/dist/rules";

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

  public valid = true;
  public password1 = "";
  public password2 = "";

  get userProfile() {
    return readUserProfile(this.$store);
  }

  public onReset() {
    this.password1 = "";
    this.password2 = "";
    this.$refs.observer.reset();
  }

  public cancel() {
    this.$router.back();
  }

  public async onSubmit() {
    const success = await this.$refs.observer.validate();
    if (!success) {
      return;
    }

    const updatedProfile: IUserProfileUpdate = {};
    updatedProfile.password = this.password1;
    await dispatchUpdateUserProfile(this.$store, updatedProfile);
    this.$router.push("/main/profile");
  }
}
</script>
