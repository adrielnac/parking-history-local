# Stage 1: Build
FROM node:24-slim AS builder

WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

# Stage 2: Run
FROM node:24-slim

WORKDIR /app
RUN mkdir /data
COPY --from=builder /app/package.json ./
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/node_modules ./node_modules


EXPOSE 3000
CMD ["npm", "run", "start"]