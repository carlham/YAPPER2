# syntax=docker/dockerfile:1

ARG NODE_VERSION=22.13.1

# --- Build Stage ---
FROM node:${NODE_VERSION}-slim AS builder
WORKDIR /app

# Install dependencies (npm ci is deterministic)
COPY --link package.json package-lock.json ./
RUN --mount=type=cache,target=/root/.npm \
    npm ci

# Copy the rest of the app source
COPY --link . .

# Build the React app
RUN npm run build

# --- Production Stage ---
FROM node:${NODE_VERSION}-slim AS final
WORKDIR /app

# Create a non-root user
RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser

# Copy built app and only production dependencies
COPY --from=builder /app/build ./build
COPY --from=builder /app/package.json ./
COPY --from=builder /app/node_modules ./node_modules

ENV NODE_ENV=production
ENV NODE_OPTIONS="--max-old-space-size=4096"

# Install serve globally as root before switching to non-root user
RUN npm install -g serve

# Set proper permissions
RUN mkdir -p /.npm && chown -R appuser:appgroup /.npm && chmod -R 775 /.npm
RUN chown -R appuser:appgroup /app

# Switch to non-root user
USER appuser

EXPOSE 3000
CMD ["serve", "-s", "build", "-l", "3000"]
