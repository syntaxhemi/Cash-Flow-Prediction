FROM node:22-alpine AS builder

WORKDIR /app

COPY apps/dashboard/package*.json apps/dashboard/
WORKDIR /app/apps/dashboard
RUN npm ci

COPY apps/dashboard/ .
ARG VITE_API_URL=http://localhost:8000
ENV VITE_API_URL=$VITE_API_URL
RUN npm run build

FROM nginx:1.29-alpine

COPY --from=builder /app/apps/dashboard/dist /usr/share/nginx/html

EXPOSE 80
