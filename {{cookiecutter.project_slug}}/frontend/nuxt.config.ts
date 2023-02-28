// https://v3.nuxtjs.org/api/configuration/nuxt.config
export default defineNuxtConfig({
    app: {
        head: {
          meta: [
            { charset: "utf-8" },
            // <meta name="viewport" content="width=device-width, initial-scale=1">
            { name: "viewport", content: "width=device-width, initial-scale=1" }
          ],
          script: [
            // <script src="https://myawesome-lib.js"></script>
            // { src: "@/assets/css/main.css" }
          ],
          noscript: [
            // <noscript>Javascript is required</noscript>
            { children: "Javascript is required" }
          ]
        },
        // pageTransition: { name: "page", mode: "out-in" }
      },
    runtimeConfig: {
      // https://nuxt.com/docs/api/composables/use-runtime-config#using-the-env-file
      // Private keys are only available on the server
      apiSecret: process.env.VUE_PRIVATE_TERM,
      // Public keys that are exposed to the client
      public: {
        appName: process.env.VUE_APP_NAME,
        appEnv: process.env.VUE_APP_ENV,
        apiWS: process.env.VUE_APP_DOMAIN_WS,
        apiUrl: process.env.VUE_APP_DOMAIN_API,
        // idbName: process.env.VUE_IDB_NAME,
        // idbVersion: process.env.VUE_IDB_VERSION,
      }
    },
    modules: [
        [
          "@pinia/nuxt",
          {
            autoImports: [
              // automatically imports `defineStore`
              "defineStore", // import { defineStore } from "pinia"
            ],
          },
        ],
        "@pinia-plugin-persistedstate/nuxt",
        "@nuxt/content",
        "tailwindcss"
    ],
    piniaPersistedstate: {
      cookieOptions: {
        path: "/",
        // maxAge: 60 * 60 * 24 * 30,
        secure: true,
      },
    },
    content: {
      // https://content.nuxtjs.org/api/configuration
      // @ts-ignore
      api: { baseURL: '/apc/_content' },
      navigation: {
        fields: ["title", "author", "publishedAt"]
      }
    },
    css: ["~/assets/css/main.css"],
    postcss: {
        plugins: {
            tailwindcss: {},
            autoprefixer: {},
        },
    },
    build: {
      transpile: ["@heroicons/vue"]
    }
})
