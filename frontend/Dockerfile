FROM node:18.20.4-alpine3.20 AS build

WORKDIR /app

# Optional but good security practice
RUN apk update && apk upgrade --no-cache

# Install dependencies
COPY package*.json ./
RUN npm ci

# Copy source
COPY . .

# Set environment variables for build
# ENV REACT_APP_BACKEND_URL="https://face-detection-ai-1.onrender.com"



# Build React app (CRA -> build/)
RUN npm run build


# ====================
# 2) Nginx Stage
# ====================
FROM nginx:1.27.1-alpine3.20 AS production

RUN apk update && apk upgrade --no-cache

# Copy compiled React build from previous stage
COPY --from=build /app/build /usr/share/nginx/html

# SPA routing config
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Fix permissions so nginx user can run
RUN mkdir -p /var/cache/nginx /var/run \
    && chown -R nginx:nginx /usr/share/nginx/html \
    && chown -R nginx:nginx /var/cache/nginx \
    && chown -R nginx:nginx /var/run \
    && chmod -R 755 /var/cache/nginx

# USER nginx

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]