const OFF = 0,
  WARN = 1,
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
    "shims-vue.d.ts"
  ],
  extends: [
    "plugin:vue/recommended",
    "eslint:recommended",
    "@vue/typescript/recommended",
    "@vue/prettier",
    "@vue/prettier/@typescript-eslint",
  ],
  parserOptions: {
    ecmaVersion: 2020,
  },
  rules: {
    "no-console": process.env.NODE_ENV === "production" ? ERROR : OFF,
    "no-debugger": process.env.NODE_ENV === "production" ? ERROR : OFF,
    "@typescript-eslint/interface-name-prefix": [
      WARN,
      {
        prefixWithI: "always",
      },
    ],
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
  ],
};
