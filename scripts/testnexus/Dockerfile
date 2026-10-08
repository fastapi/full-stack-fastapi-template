FROM node:22-bookworm-slim AS node
FROM oven/bun:1 AS bun
FROM ghcr.io/astral-sh/uv:0.9.26 AS uv
FROM axllent/mailpit:v1.30.2 AS mailpit
FROM python:3.14-bookworm

COPY --from=node /usr/local/bin/node /usr/local/bin/node
COPY --from=node /usr/local/lib/node_modules /usr/local/lib/node_modules
COPY --from=bun /usr/local/bin/bun /usr/local/bin/bun
COPY --from=uv /uv /usr/local/bin/uv
COPY --from=mailpit /mailpit /usr/local/bin/mailpit
RUN ln -s /usr/local/lib/node_modules/npm/bin/npm-cli.js /usr/local/bin/npm \
    && ln -s /usr/local/lib/node_modules/npm/bin/npx-cli.js /usr/local/bin/npx \
    && ln -s /usr/local/bin/bun /usr/local/bin/bunx \
    && apt-get update \
    && apt-get install -y --no-install-recommends git ca-certificates less \
    && rm -rf /var/lib/apt/lists/*
ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright
ENV UV_PYTHON_DOWNLOADS=never
RUN npm install --prefix /opt/testnexus --no-audit --no-fund @playwright/test@1.63.0 \
    && /opt/testnexus/node_modules/.bin/playwright install --with-deps chromium \
    && chmod -R a+rX /ms-playwright \
    && rm -rf /var/lib/apt/lists/* /root/.npm
USER 65532:65532
WORKDIR /workspace
