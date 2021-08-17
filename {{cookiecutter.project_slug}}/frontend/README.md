# Nuxt.js frontend replacement for FastAPI base project generator

## What is it?

Accelerate your next FastAPI Base Project Generator frontend development by replacing Vue.js with NuxtJS, an open source framework making web development simple and powerful.

## Build Setup

### Project

First deploy FastAPI's [Base Project Generator](https://github.com/tiangolo/full-stack-fastapi-postgresql), then replace the entire `frontend` folder with this one, updating the `.env` settings, and `nuxt.config.js`, and `package.json` <i>'frontend'</i> project name with your own.

### Yarn

```bash
# install dependencies
$ yarn install

# serve with hot reload at localhost:3000
$ yarn dev

# build for production and launch server
$ yarn build
$ yarn start

# generate static project
$ yarn generate
```

Hot reload does not work in WSL2 (only WSL1, as of 1 April 2021). For detailed explanation on how things work, check out [Nuxt.js docs](https://nuxtjs.org).

### Docker

A [Docker](https://www.docker.com/) configuration is also provided. The _Dockerfile_ is divided into four [build stages](https://docs.docker.com/develop/develop-images/multistage-build/):

1. `build`:
   - Copy files from the repo into the Docker container
   - Install dependencies from _package.json_ with Yarn
   - Build the Nuxt.js app with [server-side rendering](https://nuxtjs.org/docs/2.x/concepts/server-side-rendering) (SSR) in [standalone mode](https://nuxtjs.org/docs/2.x/configuration-glossary/configuration-build#standalone)
2. `run-dev`: use the build stage to run the dev server, which can hot-reload within the Docker container if the source code is mounted
3. `run-start`: use the build stage to run [`nuxt start`](https://nuxtjs.org/docs/2.x/get-started/commands), with all dependencies from the build
4. `run-minimal`: this image is less than 1/6 the size of the others (262 MB vs. 1.72 GB)
   - Pull a Node.js image running on Alpine Linux
   - Copy the built Nuxt.js app from the `build` stage, without `node_modules`
   - Install `nuxt-start`, with the minimal runtime for Nuxt.js (needed in addition to the inlined dependencies from standalone mode)
   - Run the `nuxt start` command using the `nuxt-start` module to start the SSR application

**Important note:** The main trade-off for the minimal production build is that any NuxtJS modules declared in the [`modules:` section of the _nuxt.config.js_ file](https://github.com/whythawk/full-stack-fastapi-postgresql/blob/ee12a3ffe3288163c7ce1e20ceae7e694213116d/%7B%7Bcookiecutter.project_slug%7D%7D/frontend/nuxt.config.js#L51-L60) must also be specified in the _Dockerfile_ on the `yarn add` line as shown [here](https://github.com/whythawk/full-stack-fastapi-postgresql/blob/ee12a3ffe3288163c7ce1e20ceae7e694213116d/%7B%7Bcookiecutter.project_slug%7D%7D/frontend/Dockerfile#L22) (it's not installing from the _package.json_, which is one reason why it's smaller). To switch from the minimal production build to the full production build, either specify the [target build stage](https://docs.docker.com/compose/compose-file/compose-file-v3/#target) in the _docker-compose.yml_ (`target: run-start`, as is done for the local development configuration [here](https://github.com/whythawk/full-stack-fastapi-postgresql/blob/ee12a3ffe3288163c7ce1e20ceae7e694213116d/%7B%7Bcookiecutter.project_slug%7D%7D/docker-compose.override.yml#L83-L85)), or push Docker images from each stage to a registry, then specify the appropriate tag to be pulled (with the `TAG` environment variable, as shown [here](https://github.com/whythawk/full-stack-fastapi-postgresql/blob/ee12a3ffe3288163c7ce1e20ceae7e694213116d/%7B%7Bcookiecutter.project_slug%7D%7D/docker-compose.yml#L225-L229)).

To work with the Docker configuration:

```sh
cd /path/to/full-stack-fastapi-postgresql/{{cookiecutter.project_slug}}/frontend

# build and run the development environment with hot-reloading
docker build . --rm --target run-dev -t localhost/whythawk/nuxt-for-fastapi:run-dev
docker run -it -p 3000:3000 -v $(pwd):/app --env-file $(pwd)/.env localhost/whythawk/nuxt-for-fastapi:run-dev

# build and run the minimal production environment
docker build . --rm --target run-minimal -t localhost/whythawk/nuxt-for-fastapi:run-minimal
docker run --env-file $(pwd)/.env -it -p 3000:3000 localhost/whythawk/nuxt-for-fastapi:run-minimal
```

Then browse to http://localhost:3000 to see the homepage.

## Nuxt.js and components

- [Nuxt.js](https://nuxtjs.org/)
- [Nuxt-property-decorator](https://github.com/nuxt-community/nuxt-property-decorator)
- [Vue Class Component](https://class-component.vuejs.org/)

## TailwindCSS

- [Tailwindcss](https://tailwindcss.com/)
- [Tailwind heroicons](https://heroicons.com/)
- [Tailwind typography](https://github.com/tailwindlabs/tailwindcss-typography)

## Helpers

- [Nuxt/content](https://content.nuxtjs.org/)
- [Vee-validate](https://vee-validate.logaretm.com/v3/)
- [Nuxt/PWA](https://pwa.nuxtjs.org/)

Nuxt/PWA is a zero config PWA solution:

- Registers a service worker for offline caching.
- Automatically generate manifest.json file.
- Automatically adds SEO friendly meta data with manifest integration.
- Automatically generates app icons with different sizes.
- Free background push notifications using OneSignal.

## Licence

This project is licensed under the terms of the MIT license.
