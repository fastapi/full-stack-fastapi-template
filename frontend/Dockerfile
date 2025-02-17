# Build-stage based on Node.js, to build and compile the frontend
FROM node:20 AS build-stage

WORKDIR /app

COPY package*.json /app/

RUN npm install

COPY ./ /app/

ARG VITE_API_URL=${VITE_API_URL}

# Development Stage: Used for Live Reload (`npm run dev`)
FROM build-stage AS development
# Expose Vite's default port
EXPOSE 5173
CMD ["npm", "run", "dev"] 

# Production Stage: Only Used in Production
FROM build-stage AS production-build
RUN npm run build 

# Stage based on Nginx, to have only the compiled app, ready for production with Nginx
FROM nginx:1 as production
COPY --from=production-build /app/dist/ /usr/share/nginx/html
COPY ./nginx.conf /etc/nginx/conf.d/default.conf
COPY ./nginx-backend-not-found.conf /etc/nginx/extra-conf.d/backend-not-found.conf