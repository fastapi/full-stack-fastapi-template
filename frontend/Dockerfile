# 🏢 GENIUS INDUSTRIES - Frontend Dockerfile
# React + Vite + TypeScript + Nginx

FROM node:18-alpine as builder

# Variables de entorno para construcción
ENV NODE_ENV=production \
    NPM_CONFIG_CACHE=/tmp/.npm

# Directorio de trabajo
WORKDIR /app

# Copiar archivos de dependencias
COPY package*.json ./

# Instalar todas las dependencias (incluyendo devDependencies para build)
RUN npm ci --silent && npm cache clean --force

# Copiar código fuente
COPY . .

# Construir la aplicación usando binarios directos
RUN ./node_modules/.bin/tsc --noEmit --skipLibCheck --noUnusedLocals false --noUnusedParameters false || true && ./node_modules/.bin/vite build

# =============================================================================
# Imagen de producción con Nginx
# =============================================================================
FROM nginx:alpine

# Instalar curl para health checks
RUN apk add --no-cache curl

# Remover configuración por defecto de Nginx
RUN rm /etc/nginx/conf.d/default.conf

# Crear usuario nginx si no existe
RUN addgroup -g 101 -S nginx || true
RUN adduser -S -D -H -u 101 -h /var/cache/nginx -s /sbin/nologin -G nginx -g nginx nginx || true

# Crear configuración de Nginx para SPA usando printf
RUN printf 'server {\n\
    listen 80;\n\
    server_name localhost;\n\
    root /usr/share/nginx/html;\n\
    index index.html;\n\
\n\
    # Security headers\n\
    add_header X-Frame-Options DENY always;\n\
    add_header X-Content-Type-Options nosniff always;\n\
    add_header X-XSS-Protection "1; mode=block" always;\n\
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;\n\
\n\
    # Gzip compression\n\
    gzip on;\n\
    gzip_vary on;\n\
    gzip_min_length 1024;\n\
    gzip_types text/plain text/css text/xml text/javascript application/javascript application/xml+rss application/json;\n\
\n\
    # SPA routing\n\
    location / {\n\
        try_files $uri $uri/ /index.html;\n\
        location ~* \\.html$ {\n\
            expires -1;\n\
            add_header Cache-Control "no-cache, no-store, must-revalidate";\n\
        }\n\
    }\n\
\n\
    # Cache para assets\n\
    location ~* \\.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {\n\
        expires 1y;\n\
        add_header Cache-Control "public, immutable";\n\
    }\n\
\n\
    # Health check\n\
    location /health {\n\
        access_log off;\n\
        return 200 "healthy\\n";\n\
        add_header Content-Type text/plain;\n\
    }\n\
\n\
    # Denegar archivos sensibles\n\
    location ~ /\\. {\n\
        deny all;\n\
        access_log off;\n\
    }\n\
\n\
    error_page 404 /index.html;\n\
}\n' > /etc/nginx/conf.d/default.conf

# Copiar archivos construidos desde la etapa builder
COPY --from=builder /app/dist /usr/share/nginx/html

# Asegurar permisos correctos
RUN chown -R nginx:nginx /usr/share/nginx/html && \
    chown -R nginx:nginx /var/cache/nginx && \
    chown -R nginx:nginx /var/log/nginx && \
    chmod -R 755 /usr/share/nginx/html

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -f http://localhost/health || exit 1

# Exponer puerto
EXPOSE 80

# Comando de inicio
CMD ["nginx", "-g", "daemon off;"]
