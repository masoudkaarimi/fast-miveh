# --- Base Stage (Common for both dev and prod) ---
FROM node:20-alpine AS base
WORKDIR /app
RUN addgroup -g 1001 -S nodejs && \
    adduser -S nextjs -u 1001
COPY --chown=nextjs:nodejs package*.json ./

# --- Development Stage ---
FROM base AS development
USER root
RUN npm install
USER nextjs
CMD ["npm", "run", "dev"]

# --- Production Build Stage ---
FROM base AS production-builder
USER root
RUN npm install
COPY --chown=nextjs:nodejs . .
RUN npm run build

# --- Final Production Stage ---
FROM base AS production
COPY --from=production-builder --chown=nextjs:nodejs /app/.next ./.next
COPY --from=production-builder /app/public ./public
USER root
RUN npm install --only=production
USER nextjs
CMD ["npm", "start"]