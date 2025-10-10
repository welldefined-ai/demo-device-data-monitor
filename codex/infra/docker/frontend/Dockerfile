# Placeholder Dockerfile for frontend app
FROM node:20-alpine AS build
WORKDIR /app
COPY frontend/package.json frontend/tsconfig.json frontend/vite.config.ts /app/
COPY frontend/src /app/src
COPY frontend/index.html /app/index.html
RUN npm ci || true && npm run build || true

FROM nginx:1.27-alpine AS runtime
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80

