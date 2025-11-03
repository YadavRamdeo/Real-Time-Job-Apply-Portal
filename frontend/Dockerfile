# Frontend Dockerfile
FROM node:20-alpine

WORKDIR /app/frontend

# Install dependencies (cache layer)
COPY frontend/package*.json ./
RUN npm install

# Copy source
COPY frontend ./

EXPOSE 3000

# Start CRA dev server
CMD ["npm", "start"]
