import Vue from "vue"
import { ValidationObserver, ValidationProvider, extend } from "vee-validate"
import { required, confirmed, email } from "vee-validate/dist/rules"

extend("required", {
  ...required,
  message: "true",
})

extend("confirmed", {
  ...confirmed,
  message: "true",
})

extend("email", {
  ...email,
  message: "Please use a valid email address.",
})

// Register it globally
Vue.component("ValidationProvider", ValidationProvider)
Vue.component("ValidationObserver", ValidationObserver)
