#!/bin/sh

# Script de entrada para el contenedor frontend de GENIUS INDUSTRIES

echo "🚀 Iniciando Frontend de GENIUS INDUSTRIES..."

# Reemplazar variables de entorno en tiempo de ejecución si es necesario
if [ ! -z "$API_URL" ]; then
    echo "📡 Configurando API URL: $API_URL"
    find /usr/share/nginx/html -name "*.js" -exec sed -i "s|REPLACE_API_URL|$API_URL|g" {} \;
fi

if [ ! -z "$CLERK_PUBLISHABLE_KEY" ]; then
    echo "🔑 Configurando Clerk Key"
    find /usr/share/nginx/html -name "*.js" -exec sed -i "s|REPLACE_CLERK_KEY|$CLERK_PUBLISHABLE_KEY|g" {} \;
fi

echo "✅ Frontend configurado correctamente"

# Ejecutar comando principal
exec "$@" 