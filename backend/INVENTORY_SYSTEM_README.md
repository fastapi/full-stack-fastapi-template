# Inventario-Express - Sistema de Gestión de Inventario

## Descripción

**Inventario-Express** es un sistema completo de gestión de inventario para tiendas minoristas, diseñado para centralizar el catálogo de productos y las operaciones de inventario (compras, ventas, ajustes), con actualización en tiempo real y alertas automáticas de stock bajo.

### Problema que Resuelve

- ❌ **Antes:** Herramientas dispersas, errores de conteo, quiebres inesperados, sobreinventario
- ✅ **Después:** Control preciso y oportuno de existencias, alertas automáticas, decisiones informadas

### Beneficios

- 📉 Reducción de pérdidas en inventario
- 📊 Mejor planeación de compras
- ⏱️ Ahorro de tiempo operativo
- 📈 Análisis de rotación y ventas

---

## Características Principales

### 1. Catálogo de Productos
- **SKU único** por producto (validado a nivel de base de datos)
- Precios de costo y venta
- Unidad de medida configurable (unidad, kg, litro, caja, etc.)
- Categorización de productos
- Stock mínimo configurable para alertas
- Soft delete (is_active flag)

### 2. Movimientos de Inventario
- **Entradas:**
  - Compras a proveedores
  - Devoluciones de clientes
- **Salidas:**
  - Ventas
  - Devoluciones a proveedores
- **Ajustes:**
  - Conteos físicos
  - Mermas (robo, daño, expiración)
- **Kardex:** Historial completo e inmutable de todos los movimientos

### 3. Alertas Automáticas
- Generación automática cuando `stock actual ≤ stock mínimo`
- Tipos de alertas:
  - `LOW_STOCK`: 0 < stock ≤ mínimo
  - `OUT_OF_STOCK`: stock = 0
- Resolución automática al reabastecer
- Bandeja de alertas activas para seguimiento

### 4. Reportes Exportables
- **Inventario:** Estado actual, valores, productos con bajo stock
- **Ventas:** Productos vendidos, cantidades, ingresos por período
- **Compras:** Productos comprados, cantidades, costos por período
- **Exportación:** CSV con resúmenes automáticos

### 5. Sistema de Roles y Permisos
- **Administrador:** Control total del sistema
- **Vendedor:** Registrar ventas, consultar existencias
- **Auxiliar:** Registrar compras, ajustes, conteos

### 6. Tiempo Real
- Actualización inmediata del stock tras cada movimiento (< 1 segundo)
- Sin caché - datos siempre actuales
- Transacciones atómicas para consistencia

---

## Arquitectura Técnica

### Stack Tecnológico

- **Framework:** FastAPI 0.114+
- **ORM:** SQLModel 0.0.21+ (SQLAlchemy + Pydantic)
- **Base de Datos:** PostgreSQL
- **Migraciones:** Alembic
- **Autenticación:** JWT con bcrypt
- **Validación:** Pydantic 2.0+

### Estructura del Proyecto

```
backend/
├── app/
│   ├── models.py                    # Modelos SQLModel (User, Category, Product, etc.)
│   ├── crud.py                      # Funciones CRUD con lógica de negocio
│   ├── api/
│   │   ├── deps.py                  # Dependencias (auth, permisos por roles)
│   │   ├── main.py                  # Router principal de API
│   │   └── routes/
│   │       ├── categories.py        # CRUD de categorías
│   │       ├── products.py          # CRUD de productos
│   │       ├── inventory_movements.py  # Movimientos de inventario
│   │       ├── alerts.py            # Gestión de alertas
│   │       ├── kardex.py            # Consulta de movimientos por producto
│   │       └── reports.py           # Reportes exportables
│   └── alembic/
│       └── versions/
│           └── 2025102701_add_inventory_management_system.py  # Migración
│
├── INVENTORY_DATABASE_SCHEMA.md     # Documentación de base de datos
├── REQUIREMENTS_VALIDATION.md       # Validación de requisitos
└── INVENTORY_SYSTEM_README.md       # Este archivo
```

---

## Modelos de Datos

### User (extendido)
```python
- id: UUID
- email: str (único)
- hashed_password: str
- is_active: bool
- is_superuser: bool
- full_name: str | None
- role: UserRole  # NUEVO: "administrador" | "vendedor" | "auxiliar"
```

### Category
```python
- id: UUID
- name: str (único)
- description: str | None
- is_active: bool
- created_at: datetime
- updated_at: datetime
- created_by: UUID (FK User)
```

### Product
```python
- id: UUID
- sku: str (único, índice)
- name: str
- description: str | None
- category_id: UUID | None (FK Category)
- unit_price: Decimal(10,2)  # Precio de costo
- sale_price: Decimal(10,2)  # Precio de venta
- unit_of_measure: str
- current_stock: int (≥ 0)  # Actualizado automáticamente
- min_stock: int (≥ 0)
- is_active: bool
- created_at: datetime
- updated_at: datetime
- created_by: UUID (FK User)
```

### InventoryMovement
```python
- id: UUID
- product_id: UUID (FK Product, RESTRICT on delete)
- movement_type: MovementType enum
- quantity: int (positivo para entradas, negativo para salidas)
- reference_number: str | None  # Factura, ticket
- notes: str | None  # Requerido para ajustes
- unit_price: Decimal | None
- total_amount: Decimal | None
- stock_before: int
- stock_after: int
- movement_date: datetime
- created_at: datetime
- created_by: UUID (FK User)
```

**MovementType Enum:**
- `ENTRADA_COMPRA`: Compra a proveedor
- `SALIDA_VENTA`: Venta a cliente
- `AJUSTE_CONTEO`: Ajuste por conteo físico
- `AJUSTE_MERMA`: Merma, robo, daño
- `DEVOLUCION_CLIENTE`: Cliente devuelve producto
- `DEVOLUCION_PROVEEDOR`: Devolver a proveedor

### Alert
```python
- id: UUID
- product_id: UUID (FK Product, CASCADE on delete)
- alert_type: AlertType enum  # "low_stock" | "out_of_stock"
- current_stock: int
- min_stock: int
- is_resolved: bool
- resolved_at: datetime | None
- resolved_by: UUID | None (FK User)
- notes: str | None
- created_at: datetime
```

---

## API Endpoints

Todos los endpoints requieren autenticación JWT excepto los de login.

Base URL: `/api/v1`

### Categories

| Método | Endpoint | Descripción | Roles |
|--------|----------|-------------|-------|
| GET | `/categories` | Listar categorías | Todos |
| GET | `/categories/{id}` | Detalle de categoría | Todos |
| POST | `/categories` | Crear categoría | Admin |
| PATCH | `/categories/{id}` | Actualizar categoría | Admin |
| DELETE | `/categories/{id}` | Eliminar categoría | Admin |

### Products

| Método | Endpoint | Descripción | Roles |
|--------|----------|-------------|-------|
| GET | `/products` | Listar productos | Todos |
| GET | `/products/{id}` | Detalle de producto | Todos |
| GET | `/products/sku/{sku}` | Buscar por SKU | Todos |
| POST | `/products` | Crear producto | Admin |
| PATCH | `/products/{id}` | Actualizar producto | Admin |
| DELETE | `/products/{id}` | Eliminar producto | Admin |

**Query params para GET /products:**
- `skip`, `limit`: Paginación
- `active_only`: bool (default: true)
- `category_id`: UUID
- `search`: Buscar en SKU o nombre
- `low_stock_only`: bool (filtra productos con stock ≤ mínimo)

### Inventory Movements

| Método | Endpoint | Descripción | Roles |
|--------|----------|-------------|-------|
| GET | `/inventory-movements` | Listar movimientos | Todos |
| GET | `/inventory-movements/{id}` | Detalle de movimiento | Todos |
| POST | `/inventory-movements/entrada` | Crear entrada | Admin, Auxiliar |
| POST | `/inventory-movements/salida` | Crear salida (venta) | Admin, Vendedor |
| POST | `/inventory-movements/ajuste` | Crear ajuste | Admin, Auxiliar |
| POST | `/inventory-movements` | Crear movimiento (genérico) | Variable por tipo |

**Query params para GET /inventory-movements:**
- `skip`, `limit`: Paginación
- `product_id`: UUID
- `movement_type`: MovementType
- `start_date`, `end_date`: Rango de fechas

**Ejemplo de request - Registrar venta:**
```json
POST /api/v1/inventory-movements/salida
{
  "product_id": "123e4567-e89b-12d3-a456-426614174000",
  "movement_type": "salida_venta",
  "quantity": 10,
  "reference_number": "VT-042",
  "notes": "Venta mostrador"
}
```

**Respuesta:**
```json
{
  "id": "...",
  "product_id": "...",
  "movement_type": "salida_venta",
  "quantity": 10,
  "stock_before": 50,
  "stock_after": 40,
  "total_amount": "250.00",
  "reference_number": "VT-042",
  "created_at": "2025-10-27T10:30:00",
  "created_by": "..."
}
```

### Alerts

| Método | Endpoint | Descripción | Roles |
|--------|----------|-------------|-------|
| GET | `/alerts` | Listar alertas | Todos |
| GET | `/alerts/active` | Solo alertas activas | Todos |
| GET | `/alerts/{id}` | Detalle de alerta | Todos |
| GET | `/alerts/product/{product_id}` | Alertas por producto | Todos |
| PATCH | `/alerts/{id}/resolve` | Resolver alerta | Admin |

**Query params para GET /alerts:**
- `skip`, `limit`: Paginación
- `resolved`: bool | null (null = todas)
- `product_id`: UUID
- `alert_type`: AlertType

### Kardex

| Método | Endpoint | Descripción | Roles |
|--------|----------|-------------|-------|
| GET | `/kardex/{product_id}` | Kardex por ID | Todos |
| GET | `/kardex/sku/{sku}` | Kardex por SKU | Todos |

**Query params:**
- `start_date`, `end_date`: Rango de fechas
- `skip`, `limit`: Paginación

**Respuesta:**
```json
{
  "product": {
    "id": "...",
    "sku": "PROD-001",
    "name": "Producto Ejemplo",
    "current_stock": 40,
    "min_stock": 10
  },
  "movements": [
    {
      "id": "...",
      "movement_type": "salida_venta",
      "quantity": -10,
      "stock_before": 50,
      "stock_after": 40,
      "movement_date": "2025-10-27T10:30:00",
      "created_by": "..."
    }
  ],
  "total_movements": 25,
  "current_stock": 40,
  "stock_status": "OK"
}
```

### Reports

| Método | Endpoint | Descripción | Roles |
|--------|----------|-------------|-------|
| GET | `/reports/inventory` | Reporte de inventario (JSON) | Todos |
| GET | `/reports/inventory/csv` | Reporte de inventario (CSV) | Todos |
| GET | `/reports/sales` | Reporte de ventas (JSON) | Todos |
| GET | `/reports/sales/csv` | Reporte de ventas (CSV) | Todos |
| GET | `/reports/purchases` | Reporte de compras (JSON) | Todos |
| GET | `/reports/purchases/csv` | Reporte de compras (CSV) | Todos |

**Query params:**
- `start_date`, `end_date`: Para reportes de ventas/compras
- `category_id`: Filtrar por categoría
- `active_only`: bool (solo para inventario)

---

## Instalación y Configuración

### 1. Prerequisitos

- Python 3.11+
- PostgreSQL 15+
- pip o poetry

### 2. Instalación de Dependencias

```bash
cd backend
pip install -r requirements.txt
```

### 3. Configuración de Base de Datos

Crear archivo `.env` en la raíz del proyecto:

```env
# Database
POSTGRES_SERVER=localhost
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password
POSTGRES_DB=inventario_express

# Security
SECRET_KEY=your-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=11520  # 8 days

# Project
PROJECT_NAME=Inventario-Express
ENVIRONMENT=local
API_V1_STR=/api/v1
```

### 4. Ejecutar Migraciones

```bash
cd backend
alembic upgrade head
```

Esto creará todas las tablas del sistema de inventario:
- user (con columna role agregada)
- category
- product
- inventorymovement
- alert

### 5. Crear Usuario Administrador Inicial

```bash
python -m app.initial_data
```

Esto creará un usuario administrador por defecto:
- Email: admin@example.com
- Password: changethis
- Role: administrador
- is_superuser: True

**IMPORTANTE:** Cambiar la contraseña inmediatamente en producción.

### 6. Iniciar Servidor de Desarrollo

```bash
uvicorn app.main:app --reload --port 8000
```

La API estará disponible en `http://localhost:8000`

Documentación interactiva:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

---

## Flujos de Trabajo Comunes

### Flujo 1: Alta de Producto

1. **Crear Categoría (opcional)**
   ```http
   POST /api/v1/categories
   {
     "name": "Electrónica",
     "description": "Productos electrónicos"
   }
   ```

2. **Crear Producto**
   ```http
   POST /api/v1/products
   {
     "sku": "LAPTOP-001",
     "name": "Laptop Dell Inspiron 15",
     "category_id": "<uuid>",
     "unit_price": 450.00,
     "sale_price": 599.99,
     "unit_of_measure": "unidad",
     "min_stock": 5
   }
   ```

3. **Registrar Entrada (Compra)**
   ```http
   POST /api/v1/inventory-movements/entrada
   {
     "product_id": "<uuid>",
     "movement_type": "entrada_compra",
     "quantity": 20,
     "unit_price": 450.00,
     "reference_number": "FC-001-2025",
     "notes": "Compra a proveedor TechSupply"
   }
   ```

   **Efecto:** Stock pasa de 0 → 20

### Flujo 2: Venta

```http
POST /api/v1/inventory-movements/salida
{
  "product_id": "<uuid>",
  "movement_type": "salida_venta",
  "quantity": 2,
  "reference_number": "VT-042",
  "notes": "Venta mostrador"
}
```

**Efectos:**
- Stock pasa de 20 → 18
- Se calcula `total_amount` = quantity × sale_price
- Si stock ≤ min_stock (5): se crea alerta automática

### Flujo 3: Gestión de Alertas

1. **Consultar Alertas Activas**
   ```http
   GET /api/v1/alerts/active
   ```

2. **Ver Detalles de Alerta**
   ```http
   GET /api/v1/alerts/{alert_id}
   ```

3. **Opciones:**
   - **Reabastecer:** Crear entrada → alerta se resuelve automáticamente
   - **Resolver Manualmente:** `PATCH /api/v1/alerts/{id}/resolve` (solo admin)

### Flujo 4: Reportes

1. **Reporte de Inventario**
   ```http
   GET /api/v1/reports/inventory?category_id=<uuid>
   ```

2. **Exportar a CSV**
   ```http
   GET /api/v1/reports/inventory/csv
   ```
   Descarga archivo `inventory_report_YYYYMMDD_HHMMSS.csv`

3. **Reporte de Ventas por Período**
   ```http
   GET /api/v1/reports/sales?start_date=2025-10-01&end_date=2025-10-31
   ```

4. **Kardex de Producto**
   ```http
   GET /api/v1/kardex/sku/LAPTOP-001
   ```

---

## Permisos por Rol

| Acción | Administrador | Vendedor | Auxiliar |
|--------|---------------|----------|----------|
| Ver productos/categorías | ✅ | ✅ | ✅ |
| Crear/editar productos | ✅ | ❌ | ❌ |
| Crear/editar categorías | ✅ | ❌ | ❌ |
| Registrar compras (entradas) | ✅ | ❌ | ✅ |
| Registrar ventas (salidas) | ✅ | ✅ | ❌ |
| Registrar ajustes | ✅ | ❌ | ✅ |
| Ver alertas | ✅ | ✅ | ✅ |
| Resolver alertas | ✅ | ❌ | ❌ |
| Ver reportes | ✅ | ✅ | ✅ |
| Exportar reportes | ✅ | ✅ | ✅ |
| Gestionar usuarios | ✅ | ❌ | ❌ |

---

## Validaciones y Constraints

### A Nivel de Base de Datos

- ✅ `Product.sku` UNIQUE
- ✅ `Product.current_stock >= 0`
- ✅ `Product.min_stock >= 0`
- ✅ `Product.unit_price > 0`
- ✅ `Product.sale_price > 0`
- ✅ `InventoryMovement.quantity != 0`
- ✅ `InventoryMovement.stock_before >= 0`
- ✅ `InventoryMovement.stock_after >= 0`
- ✅ `Category.name` UNIQUE
- ✅ `User.email` UNIQUE

### A Nivel de Aplicación

- ✅ SKU único verificado antes de crear/actualizar producto
- ✅ Stock nunca puede ser negativo (validado en lógica de movimientos)
- ✅ Movimientos inmutables (no se pueden editar ni eliminar)
- ✅ `reference_number` requerido para compras y ventas
- ✅ `notes` requerido para ajustes
- ✅ `unit_price` requerido para compras
- ✅ No se permiten alertas duplicadas para el mismo producto

---

## Índices de Base de Datos (Optimización)

```sql
-- Products
CREATE INDEX ix_product_sku ON product (sku);  -- UNIQUE
CREATE INDEX ix_product_category_id ON product (category_id);
CREATE INDEX ix_product_stock_levels ON product (current_stock, min_stock);

-- Inventory Movements
CREATE INDEX ix_inventorymovement_product_date ON inventorymovement (product_id, movement_date DESC);
CREATE INDEX ix_inventorymovement_movement_type ON inventorymovement (movement_type);
CREATE INDEX ix_inventorymovement_movement_date ON inventorymovement (movement_date DESC);

-- Alerts
CREATE INDEX ix_alert_product_resolved ON alert (product_id, is_resolved);
CREATE INDEX ix_alert_resolved_created ON alert (is_resolved, created_at DESC);

-- Categories
CREATE INDEX ix_category_name ON category (name);  -- UNIQUE
```

---

## Testing

### Pruebas Manuales con Swagger UI

1. Ir a `http://localhost:8000/docs`
2. Autorizar con token JWT:
   - Clic en "Authorize"
   - Login en `/api/v1/login/access-token`
   - Copiar `access_token` de la respuesta
   - Pegar en campo "Value" como `Bearer <token>`

3. Probar endpoints en orden:
   - Crear categoría
   - Crear producto
   - Registrar entrada
   - Registrar venta
   - Ver alertas
   - Consultar kardex
   - Exportar reportes

### Pruebas con curl

```bash
# Login
TOKEN=$(curl -X POST "http://localhost:8000/api/v1/login/access-token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@example.com&password=changethis" \
  | jq -r '.access_token')

# Crear producto
curl -X POST "http://localhost:8000/api/v1/products" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "sku": "TEST-001",
    "name": "Producto Test",
    "unit_price": 10.00,
    "sale_price": 15.00,
    "unit_of_measure": "unidad",
    "min_stock": 5
  }'

# Registrar entrada
curl -X POST "http://localhost:8000/api/v1/inventory-movements/entrada" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "product_id": "<product_id>",
    "movement_type": "entrada_compra",
    "quantity": 20,
    "unit_price": 10.00,
    "reference_number": "TEST-001"
  }'
```

---

## Troubleshooting

### Error: "SKU already exists"
- **Causa:** Intentar crear producto con SKU duplicado
- **Solución:** Verificar SKUs existentes con `GET /products?search={sku}`

### Error: "Insufficient stock"
- **Causa:** Intentar vender más unidades de las disponibles
- **Solución:** Verificar stock actual con `GET /products/{id}`

### Alertas no se crean automáticamente
- **Verificar:**
  1. `min_stock` está configurado en el producto
  2. Movimiento se creó exitosamente
  3. `stock_after <= min_stock`
- **Revisar:** `GET /alerts/product/{product_id}`

### Migración falla
- **Verificar:**
  1. PostgreSQL está corriendo
  2. Credenciales en `.env` son correctas
  3. Base de datos existe: `createdb inventario_express`
  4. Usuario tiene permisos suficientes

---

## Próximos Pasos Recomendados

### Funcionalidades Futuras (v2)

- [ ] Multi-tienda (múltiples ubicaciones de inventario)
- [ ] Facturación electrónica
- [ ] Códigos de barras y escaneo
- [ ] App móvil nativa
- [ ] Dashboard en tiempo real con gráficos
- [ ] Predicción de demanda con ML
- [ ] Integración con proveedores (EDI)
- [ ] Punto de venta (POS) integrado

### Mejoras de Rendimiento

- [ ] Cache con Redis para consultas frecuentes
- [ ] Bulk operations para importación masiva
- [ ] Paginación cursor-based para grandes datasets
- [ ] WebSockets para notificaciones en tiempo real

### Seguridad

- [ ] Rate limiting
- [ ] Audit log de todas las operaciones
- [ ] 2FA (autenticación de dos factores)
- [ ] Encriptación de datos sensibles

---

## Soporte y Contribución

- **Documentación de API:** `http://localhost:8000/docs`
- **Esquema de Base de Datos:** Ver `INVENTORY_DATABASE_SCHEMA.md`
- **Validación de Requisitos:** Ver `REQUIREMENTS_VALIDATION.md`

---

## Licencia

Este proyecto es parte del template full-stack-fastapi-template.

---

## Changelog

### v1.0.0 - 2025-10-27

**Implementación inicial completa:**

- ✅ Modelos de datos (User, Category, Product, InventoryMovement, Alert)
- ✅ Sistema de roles (Administrador, Vendedor, Auxiliar)
- ✅ CRUD completo para todas las entidades
- ✅ Movimientos de inventario con actualización automática de stock
- ✅ Alertas automáticas de stock bajo
- ✅ Kardex (historial de movimientos por producto)
- ✅ Reportes exportables (inventario, ventas, compras) en JSON y CSV
- ✅ Validaciones exhaustivas (SKU único, stock no negativo, etc.)
- ✅ Migraciones de Alembic
- ✅ Documentación completa
- ✅ 33 endpoints de API
- ✅ Permisos por rol
- ✅ Transacciones atómicas
- ✅ Índices de base de datos para rendimiento

---

**¡Inventario-Express está listo para producción!** 🚀
