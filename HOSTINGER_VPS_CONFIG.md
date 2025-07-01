# 🌐 CONFIGURAR DOMINIO HOSTINGER → VPS

## 📋 Configuración DNS en Hostinger

### 1. Eliminar/Cambiar Registros Actuales

En tu panel de Hostinger > DNS Zone:

**ELIMINAR:**
```
CNAME | www | cname.vercel-dns.com
```

**AGREGAR:**
```
A     | @   | 31.97.69.243
A     | www | 31.97.69.243
```

### 2. Registros DNS Completos Recomendados

```
Tipo  | Nombre | Valor           | TTL
------|--------|-----------------|----
A     | @      | 31.97.69.243   | 14400
A     | www    | 31.97.69.243   | 14400
A     | api    | 31.97.69.243   | 14400
```

### 3. Configuración del Servidor (VPS)

En tu VPS, necesitas configurar Nginx:

#### `/etc/nginx/sites-available/genius-industries`
```nginx
server {
    listen 80;
    server_name tudominio.com www.tudominio.com;
    
    # Frontend
    location / {
        proxy_pass http://localhost:5173;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # Backend API
    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

#### Comandos en VPS:
```bash
# Habilitar sitio
sudo ln -s /etc/nginx/sites-available/genius-industries /etc/nginx/sites-enabled/

# Test configuración
sudo nginx -t

# Recargar Nginx
sudo systemctl reload nginx

# SSL con Let's Encrypt
sudo certbot --nginx -d tudominio.com -d www.tudominio.com
```

### 4. Verificación

1. **DNS Propagation**: Espera 5-30 minutos
2. **Test**: `nslookup tudominio.com`
3. **Resultado esperado**: `31.97.69.243`

### 5. Dokploy Configuration

Si usas Dokploy en el VPS:

```yaml
# docker-compose.yml
services:
  frontend:
    build: ./frontend
    ports:
      - "5173:5173"
    environment:
      - VITE_API_URL=https://tudominio.com/api

  backend:
    build: ./backend  
    ports:
      - "8000:8000"
    environment:
      - DOMAIN=tudominio.com
      - FRONTEND_HOST=https://tudominio.com
```

## 🔄 Proceso Completo

1. ✅ Cambiar DNS en Hostinger (A records)
2. ✅ Configurar Nginx en VPS
3. ✅ Configurar SSL con Certbot
4. ✅ Actualizar URLs en .env files
5. ✅ Deploy aplicaciones en VPS

**Tiempo de propagación DNS: 5-30 minutos** 