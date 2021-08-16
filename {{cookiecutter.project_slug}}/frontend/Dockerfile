FROM node:lts AS build
ENV NODE_ENV=development NUXT_HOST=${NUXT_HOST:-0.0.0.0} NUXT_PORT=${NUXT_PORT:-3000} NUXT_TELEMETRY_DISABLED=1
COPY . /app
WORKDIR /app
RUN yarn install --frozen-lockfile --network-timeout 100000 --non-interactive
RUN yarn build --standalone
EXPOSE ${NUXT_PORT}

FROM build AS run-dev
ENTRYPOINT ["yarn"]
CMD ["dev"]

FROM build AS run-start
ENV NODE_ENV=production
ENTRYPOINT ["yarn"]
CMD ["start"]

FROM node:lts-alpine AS run-minimal
ARG NUXT_VERSION=^2.15
ENV NODE_ENV=production NUXT_HOST=${NUXT_HOST:-0.0.0.0} NUXT_PORT=${NUXT_PORT:-3000} NUXT_TELEMETRY_DISABLED=1
WORKDIR /app
RUN yarn add @nuxtjs/axios @nuxt/content @nuxtjs/pwa nuxt-i18n nuxt-start@${NUXT_VERSION}
COPY --from=build /app/.nuxt ./.nuxt
COPY --from=build /app/content ./content
COPY --from=build /app/static ./static
COPY --from=build /app/nuxt.config* /app/api.ts /app/utils.ts ./
ENTRYPOINT ["yarn"]
CMD ["nuxt-start"]
