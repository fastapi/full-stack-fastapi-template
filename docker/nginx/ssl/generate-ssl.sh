#!/bin/bash

# Crear directorio si no existe
mkdir -p ssl

# Generar certificado SSL autofirmado
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout ssl/localhost.key \
  -out ssl/localhost.crt \
  -subj "/C=US/ST=State/L=City/O=Organization/CN=localhost"

# Dar permisos adecuados
chmod 644 ssl/localhost.crt
chmod 600 ssl/localhost.key

echo "Certificados SSL generados en el directorio ssl/" 