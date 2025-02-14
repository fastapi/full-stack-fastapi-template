# Use the official Node.js image as the base image
FROM node:20-alpine

# Set the working directory
WORKDIR /app

# Copy package.json and package-lock.json to the container
COPY package*.json /app/

# Install dependencies
RUN npm install

# Copy the rest of the application files
COPY ./ /app/

# Build the Next.js application
RUN npm run build

# Expose the application on port 4000
EXPOSE 3000

# Start the application
CMD ["npm", "start"]
