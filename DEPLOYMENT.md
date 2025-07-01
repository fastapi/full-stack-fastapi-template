# 🚀 DEPLOYMENT GUIDE - GENIUS INDUSTRIES

## 📋 Pre-requisitos en tu VPS

```bash
# Conectar al VPS
ssh root@31.97.69.243

# Instalar Docker y Docker Compose
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Habilitar Docker
sudo systemctl enable docker
sudo systemctl start docker
```

## 🔧 Configuración

### 1. Clonar tu proyecto en el VPS
```bash
git clone https://github.com/tu-usuario/Genius-Industries.git
cd Genius-Industries
```

### 2. Configurar variables de entorno
```bash
# Copiar plantilla de variables
cp .env.docker .env

# Editar con tus valores reales
nano .env
```

**Variables importantes a configurar:**
- `DATABASE_URL`: Tu URL real de Railway PostgreSQL
- `CLERK_WEBHOOK_SECRET`: Tu webhook secret real de Clerk
- `SECRET_KEY`: Generar una clave secreta segura

### 3. Construir y ejecutar
```bash
# Construir todas las imágenes
docker-compose build

# Ejecutar en segundo plano
docker-compose up -d

# Ver logs
docker-compose logs -f
```

## 🌐 Configuración DNS en Hostinger

En tu panel de Hostinger > DNS Zone:

```
A | @ | 31.97.69.243
A | www | 31.97.69.243
A | api | 31.97.69.243
```

## 🔒 SSL (Let's Encrypt)

```bash
# Instalar Certbot
sudo apt install certbot python3-certbot-nginx -y

# Parar nginx temporal
docker-compose stop nginx

# Obtener certificado
sudo certbot certonly --standalone -d geniusindustries.org -d www.geniusindustries.org

# Crear directorio SSL
mkdir -p nginx/ssl
sudo cp /etc/letsencrypt/live/geniusindustries.org/fullchain.pem nginx/ssl/
sudo cp /etc/letsencrypt/live/geniusindustries.org/privkey.pem nginx/ssl/

# Reiniciar servicios
docker-compose up -d
```

## ✅ Verificación

```bash
# Estado de contenedores
docker-compose ps

# Logs de backend
docker-compose logs backend

# Logs de frontend
docker-compose logs frontend

# Test de conectividad
curl -I http://geniusindustries.org
curl -I http://geniusindustries.org/api/health
```

## 🔄 Actualizaciones

```bash
# Actualizar código
git pull

# Reconstruir y reiniciar
docker-compose build
docker-compose up -d

# Limpiar imágenes antiguas
docker image prune -f
```

## 🆘 Troubleshooting

### Error de conexión a base de datos:
- Verificar `DATABASE_URL` en `.env`
- Comprobar conectividad: `docker-compose exec backend ping postgres-production-bff4.up.railway.app`

### Error 502 Bad Gateway:
- Verificar logs: `docker-compose logs nginx backend frontend`
- Verificar puertos: `docker-compose ps`

### Error de Clerk:
- Verificar claves en `.env`
- Comprobar webhook URL en Clerk Dashboard

## 🎯 URLs Finales

- **Frontend**: https://geniusindustries.org
- **Backend API**: https://geniusindustries.org/api/
- **API Docs**: https://geniusindustries.org/docs
- **Health Check**: https://geniusindustries.org/api/health 