FROM node:20

WORKDIR /app

# Copy package.json and lock file
COPY react-app/package.json ./

# Install dependencies inside the container
RUN npm install

# Copy the rest of the code (excluding node_modules due to .dockerignore)
COPY react-app/ .

EXPOSE 3000
CMD ["npm", "start"]
