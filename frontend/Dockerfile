# Stage 0, "build-stage", based on Node.js, to build and compile the frontend
FROM node:20 as build-stage

WORKDIR /app

COPY package*.json /app/

RUN npm install

COPY ./ /app/

ARG VITE_API_URL=http://localhost
# keep it like that!  The final URL will be replaced dynamically by docker-entry.sh (see below)

RUN npm run build

# Stage 1, based on Nginx, to have only the compiled app, ready for production with Nginx
FROM nginx:1

COPY --from=build-stage /app/dist/ /usr/share/nginx/html

COPY ./nginx-traefik.conf /etc/nginx/conf.d/nginx-traefik.conf
COPY ./nginx-standalone.conf /etc/nginx/conf.d/nginx-standalone.conf
# .. docker-entry.sh will copy either of those two files into into default.conf
COPY ./nginx-backend-not-found.conf /etc/nginx/extra-conf.d/backend-not-found.conf

COPY ./docker-entry.sh /docker-entry.sh

ENTRYPOINT ["/docker-entry.sh"]
# CMD ["nginx", "-g", "daemon off;"]
