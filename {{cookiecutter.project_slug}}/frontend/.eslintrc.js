const OFF = 0,
  ERROR = 2;

module.exports = {
  root: true,
  env: {
    node: true,
  },
  ignorePatterns: [
    "!.eslintrc.js",
    "!.prettierrc.js",
    "node_modules/",
    "shims-tsx.d.ts",
    "shims-vue.d.ts",
  ],
  extends: [
    "eslint:recommended",
    "plugin:@typescript-eslint/recommended",
    "plugin:vue/recommended",
    "@vue/eslint-config-typescript/recommended",
    "plugin:prettier/recommended",
  ],
  parserOptions: {
    ecmaVersion: 2020,
  },
  rules: {
    "no-console":
      process.env.NODE_ENV === "production" ? [ERROR, { allow: ["error"] }] : OFF,
    "no-debugger": process.env.NODE_ENV === "production" ? ERROR : OFF,
    "@typescript-eslint/explicit-module-boundary-types": OFF,
    "@typescript-eslint/no-unused-vars": [
      ERROR,
      {
        argsIgnorePattern: "^_",
        varsIgnorePattern: "^_",
      },
    ],
  },
  overrides: [
    {
      files: ["**/__tests__/*.{j,t}s?(x)", "**/tests/unit/**/*.spec.{j,t}s?(x)"],
      env: {
        jest: true,
      },
    },
    {
      files: ["**/registerServiceWorker.ts"],
      rules: {
        "no-console": OFF,
      },
    },
  ],
};
