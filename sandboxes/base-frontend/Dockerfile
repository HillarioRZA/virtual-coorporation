# Pre-Warmed Base Frontend Container for Ephemeral Sandboxes
FROM node:20-alpine

WORKDIR /app/base

# Pre-install dependencies to eliminate 'npm install' overhead during prototyping
COPY package.json ./
RUN npm install --legacy-peer-deps

# Create workspace directory where project code will be mounted
WORKDIR /app/project

# Configure Next.js fast polling for Windows volume mounting compatibility
ENV NODE_ENV=development
ENV WATCHPACK_POLLING=true
ENV PORT=3000
ENV HOSTNAME="0.0.0.0"

# Expose default dev server port
EXPOSE 3000

# Copy node_modules symlink or fallback to base node_modules if not in mounted volume
CMD ["sh", "-c", "if [ ! -d node_modules ]; then ln -s /app/base/node_modules ./node_modules; fi && npx next dev -p 3000 -H 0.0.0.0"]
