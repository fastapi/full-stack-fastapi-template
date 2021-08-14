module.exports = {
  root: true,
  env: {
    browser: true,
    node: true,
  },
  extends: [
    "@nuxtjs/eslint-config-typescript",
    "plugin:prettier/recommended",
    "plugin:nuxt/recommended",
  ],
  plugins: [],
  // add your custom rules here
  // https://allurcode.com/custom-linting-rules-in-nuxtjs-and-eslint/
  // https://stackoverflow.com/questions/53516594/why-do-i-keep-getting-delete-cr-prettier-prettier
  rules: {
    "no-console": process.env.VUE_APP_ENV === "production" ? "error" : "off",
    "no-debugger": process.env.VUE_APP_ENV === "production" ? "error" : "off",
    "prettier/prettier": [
      "error",
      {
        endOfLine: "auto",
      },
    ],
  },
}
