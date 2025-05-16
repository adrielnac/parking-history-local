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
COPY --from=builder /app/package*.json ./
COPY --from=builder /app/.next .next
RUN npm install --omit=dev


EXPOSE 3000
CMD ["npm", "start"]
