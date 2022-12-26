import { defineRule, configure } from "vee-validate";
import { required, email, min, url } from "@vee-validate/rules";
import { localize } from "@vee-validate/i18n";

export default defineNuxtPlugin((nuxtApp) => {
  defineRule("required", required);
  defineRule("email", email);
  defineRule("min", min);
  defineRule("url", url);
  defineRule("confirmed", (value, [target], ctx) => {
    // https://vee-validate.logaretm.com/v4/guide/global-validators#cross-field-validation
    if (value === ctx.form[target]) {
      return true;
    }
    return "Passwords must match.";
  });
});

configure({
  // Generates an English message locale generator
  generateMessage: localize("en", {
    messages: {
      required: "This field is required.",
      email: "This email address is invalid.",
      min: "A minimum number of characters is required.",
      url: "This url is invalid.",
    },
  }),
});

/*
  References:

  https://vee-validate.logaretm.com/v4/guide/overview/
  https://github.com/razorcx-courses/nuxt3-veevalidate
  https://vee-validate.logaretm.com/v4/guide/global-validators/#available-rules
  https://vee-validate.logaretm.com/v4/guide/i18n
*/