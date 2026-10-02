# Build stage: compile the Vite/React SPA to static files.
FROM node:20-alpine AS build

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci

COPY . .
RUN npm run build

# Runtime stage: serve the static build with nginx. A browser-side SPA
# doesn't need Node at runtime, only something to serve the files and
# fall back to index.html for client-side routing.
FROM nginx:alpine

COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
