# Multi-stage build for Laravel + Vite frontend

# Stage 1: Node.js for asset building
FROM node:20-alpine AS assets-builder
WORKDIR /app

COPY package*.json ./
RUN npm ci --prefer-offline --no-audit

COPY resources ./resources
COPY vite.config.js ./
COPY config ./config
COPY public ./public

RUN npm run build

# Stage 2: PHP dependencies
FROM composer:2.8 AS composer-builder
WORKDIR /app

COPY composer.json ./
RUN composer install --no-dev --no-interaction --no-scripts --no-autoloader --prefer-dist \
    && composer dump-autoload --no-scripts --no-dev --optimize

# Stage 3: Laravel runtime
FROM php:8.4-alpine

# Install required PHP extensions and system packages
RUN apk add --no-cache \
    curl \
    linux-headers \
    sqlite-dev \
    postgresql-dev \
    oniguruma-dev \
    libpng-dev \
    libjpeg-turbo-dev \
    libwebp-dev \
    libzip-dev \
    && docker-php-ext-configure gd --with-webp --with-jpeg \
    && docker-php-ext-install -j$(nproc) gd zip pdo_sqlite pdo_pgsql opcache sockets

# Create non-root user
RUN addgroup -g 1001 -S laravel && adduser -S laravel -u 1001 -G laravel

WORKDIR /app

# Copy PHP dependencies
COPY --from=composer-builder --chown=laravel:laravel /app/vendor ./vendor

# Copy built assets
COPY --from=assets-builder --chown=laravel:laravel /app/public/build ./public/build

# Copy application code
COPY --chown=laravel:laravel . .

# Override local .env defaults for Docker runtime networking
RUN if [ -f .env ]; then \
        sed -i 's|^API_BASE_URL=.*|API_BASE_URL=http://api-gateway|' .env; \
    sed -i 's|^API_BROWSER_BASE_URL=.*|API_BROWSER_BASE_URL=http://localhost:8080|' .env; \
    grep -q '^API_BROWSER_BASE_URL=' .env || echo 'API_BROWSER_BASE_URL=http://localhost:8080' >> .env; \
        sed -i 's|^REDIS_HOST=.*|REDIS_HOST=redis|' .env; \
        sed -i 's|^CACHE_STORE=.*|CACHE_STORE=file|' .env; \
        sed -i 's|^API_CACHE_STORE=.*|API_CACHE_STORE=file|' .env; \
        sed -i 's|^API_CACHE_ENABLED=.*|API_CACHE_ENABLED=false|' .env; \
    fi

# Remove local cached bootstrap artifacts so container uses current env/config
RUN rm -f bootstrap/cache/*.php

# Set permissions
RUN mkdir -p \
    storage \
    storage/framework/cache \
    storage/framework/sessions \
    storage/framework/views \
    storage/logs \
    bootstrap/cache \
    && chmod -R 755 storage bootstrap/cache \
    && chown -R laravel:laravel storage bootstrap/cache

# PHP optimization
RUN echo "opcache.enable=1" >> /usr/local/etc/php/conf.d/opcache.ini \
    && echo "opcache.validate_timestamps=1" >> /usr/local/etc/php/conf.d/opcache.ini \
    && echo "opcache.memory_consumption=256" >> /usr/local/etc/php/conf.d/opcache.ini

USER laravel

EXPOSE 8001

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8001/up || exit 1

# Start Laravel with php built-in server (for development)
# For production, consider using PHP-FPM + Nginx instead
CMD ["php", "artisan", "serve", "--host=0.0.0.0", "--port=8001"]
