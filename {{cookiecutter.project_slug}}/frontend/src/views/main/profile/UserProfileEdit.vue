<template>
  <v-container fluid>
    <validation-observer ref="observer" v-slot="{ invalid }">
      <form @submit.prevent="onSubmit" @reset.prevent="onReset">
        <v-card class="ma-3 pa-3">
          <v-card-title primary-title>
            <div class="headline primary--text">Edit User Profile</div>
          </v-card-title>
          <v-card-text>
            <!-- full name -->
            <validation-provider v-slot="{ errors }" name="Full Name" rules="required">
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
          </v-card-text>
          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn @click="cancel">Cancel</v-btn>
            <v-btn type="reset">Reset</v-btn>
            <v-btn type="submit" :disabled="invalid">
              Save
            </v-btn>
          </v-card-actions>
        </v-card>
      </form>
    </validation-observer>
  </v-container>
</template>

<script lang="ts">
  import { Component, Vue } from "vue-property-decorator";
  import { IUserProfileUpdate } from "@/interfaces";
  import { mainStore } from "@/store";
  import { required, email } from "vee-validate/dist/rules";
  import { ValidationProvider, ValidationObserver, extend } from "vee-validate";

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

    valid = true;
    fullName = "";
    email = "";

    created() {
      const userProfile = mainStore.userProfile;
      if (userProfile) {
        this.fullName = userProfile.full_name;
        this.email = userProfile.email;
      }
    }

    get userProfile() {
      return mainStore.userProfile;
    }

    onReset() {
      const userProfile = mainStore.userProfile;
      if (userProfile) {
        this.fullName = userProfile.full_name;
        this.email = userProfile.email;
      }
      this.$refs.observer.reset();
    }

    cancel() {
      this.$router.back();
    }

    async onSubmit() {
      const success = await this.$refs.observer.validate();

      if (!success) {
        return;
      }

      const updatedProfile: IUserProfileUpdate = {};
      if (this.fullName) {
        // eslint-disable-next-line @typescript-eslint/camelcase
        updatedProfile.full_name = this.fullName;
      }
      if (this.email) {
        updatedProfile.email = this.email;
      }
      await mainStore.updateUserProfile(updatedProfile);
      this.$router.push("/main/profile");
    }
  }
</script>
