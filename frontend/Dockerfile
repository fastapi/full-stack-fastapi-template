FROM node:24

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

ARG VITE_API_URL
RUN npm run build

EXPOSE 3000
CMD ["npm", "start"]
