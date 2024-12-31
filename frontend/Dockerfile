FROM node:20

WORKDIR /app

# Copy package.json and lock file
COPY react-app/package.json react-app/package-lock.json ./

# Install dependencies
RUN npm install

# Copy the rest of the code
COPY react-app/ .

EXPOSE 3000
CMD ["npm", "start"]
