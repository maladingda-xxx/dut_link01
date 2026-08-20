FROM node:22-slim

WORKDIR /app

# Install dependencies from the lockfile first (for caching).
COPY package.json package-lock.json ./
RUN npm ci

# Copy the rest of the application.
COPY . .

EXPOSE 5173

CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
