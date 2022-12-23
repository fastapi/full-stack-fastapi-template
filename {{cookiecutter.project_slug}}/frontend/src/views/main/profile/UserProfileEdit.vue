<template>
  <v-container fluid>
    <validation-observer ref="observer" v-slot="{ invalid }">
      <form @submit.prevent="onSubmit" @reset.prevent="onReset">
        <v-card class="ma-3 pa-3">
          <v-card-title primary-title>
            <div class="headline primary--text">Edit User Profile</div>
          </v-card-title>
          <v-card-text>
            <v-text-field v-model="fullName" label="Full Name" required></v-text-field>
            <validation-provider
              v-slot="{ errors }"
              rules="required|email"
              name="E-mail"
            >
              <v-text-field
                v-model="email"
                label="E-mail"
                type="email"
                :error-messages="errors"
                required
              ></v-text-field>
            </validation-provider>
          </v-card-text>
          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn @click="cancel">Cancel</v-btn>
            <v-btn type="reset">Reset</v-btn>
            <v-btn :disabled="invalid" type="submit"> Save </v-btn>
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
import { required, email } from "vee-validate/dist/rules";

// register validation rules
extend("required", { ...required, message: "{_field_} can not be empty" });
extend("email", { ...email, message: "Invalid email address" });

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
  public fullName = "";
  public email = "";

  public created() {
    const userProfile = readUserProfile(this.$store);
    if (userProfile) {
      this.fullName = userProfile.full_name;
      this.email = userProfile.email;
    }
  }

  get userProfile() {
    return readUserProfile(this.$store);
  }

  public onReset() {
    const userProfile = readUserProfile(this.$store);
    if (userProfile) {
      this.fullName = userProfile.full_name;
      this.email = userProfile.email;
    }
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
    if (this.fullName) {
      updatedProfile.full_name = this.fullName;
    }
    if (this.email) {
      updatedProfile.email = this.email;
    }
    await dispatchUpdateUserProfile(this.$store, updatedProfile);
    this.$router.push("/main/profile");
  }
}
</script>
