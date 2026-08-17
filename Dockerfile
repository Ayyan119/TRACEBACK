FROM node:22-alpine

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .

# Expose port
EXPOSE 3000

# Run Next.js dev server
CMD ["npm", "run", "dev"]
