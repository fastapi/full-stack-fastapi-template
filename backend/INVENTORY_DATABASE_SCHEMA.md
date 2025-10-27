# Esquema de Base de Datos - Inventario-Express

## Resumen
Sistema de gestión de inventario para tiendas minoristas con:
- Catálogo de productos con SKU único
- Movimientos de inventario (entradas, salidas, ajustes, devoluciones)
- Alertas automáticas de stock bajo
- Kardex (historial de movimientos)
- Sistema de roles (Administrador, Vendedor, Auxiliar)
- Reportes exportables

---

## 1. User (Tabla existente - EXTENDIDA)

**Propósito:** Usuarios del sistema con roles específicos

### Campos existentes:
- `id`: UUID (PK)
- `email`: str (único, índice)
- `hashed_password`: str
- `is_active`: bool (default: True)
- `is_superuser`: bool (default: False)
- `full_name`: str | None

### Campos NUEVOS:
- `role`: Enum UserRole ("administrador", "vendedor", "auxiliar") - default: "vendedor"

### Roles y permisos:
- **Administrador (administrador):**
  - Control total del sistema
  - Gestionar usuarios, productos, categorías
  - Ver todos los reportes y alertas
  - Aprobar ajustes de inventario

- **Vendedor (vendedor):**
  - Registrar ventas (salidas)
  - Consultar productos y existencias
  - Ver alertas de bajo stock
  - Reportes de ventas propias

- **Auxiliar (auxiliar):**
  - Registrar entradas (compras)
  - Realizar ajustes de inventario
  - Registrar conteos cíclicos
  - Consultar kardex

### Relaciones:
- `categories`: List[Category] (one-to-many, back_populates="created_by_user")
- `products`: List[Product] (one-to-many, back_populates="created_by_user")
- `inventory_movements`: List[InventoryMovement] (one-to-many, back_populates="created_by_user")

---

## 2. Category (NUEVA TABLA)

**Propósito:** Categorías de productos para clasificación y reportes

### Campos:
- `id`: UUID (PK)
- `name`: str (único, max_length=100, índice)
- `description`: str | None (max_length=255)
- `is_active`: bool (default: True)
- `created_at`: datetime (auto)
- `updated_at`: datetime (auto, actualizado en cada cambio)
- `created_by`: UUID (FK -> User.id, nullable=False)

### Relaciones:
- `products`: List[Product] (one-to-many, back_populates="category")
- `created_by_user`: User (many-to-one, back_populates="categories")

### Constraints:
- UNIQUE(name)
- CHECK(LENGTH(name) >= 1)

### Índices:
- PRIMARY KEY (id)
- UNIQUE INDEX (name)
- INDEX (created_by)

---

## 3. Product (NUEVA TABLA)

**Propósito:** Catálogo de productos del inventario

### Campos:
- `id`: UUID (PK)
- `sku`: str (único, max_length=50, índice) - **SKU único crítico**
- `name`: str (max_length=255)
- `description`: str | None (max_length=500)
- `category_id`: UUID | None (FK -> Category.id, nullable, on_delete=SET NULL)
- `unit_price`: Decimal(10, 2) - Precio de costo/compra
- `sale_price`: Decimal(10, 2) - Precio de venta
- `unit_of_measure`: str (max_length=50) - ej: "unidad", "kg", "litro", "caja"
- `current_stock`: int (>= 0, default: 0) - **Stock actual, se actualiza automáticamente**
- `min_stock`: int (>= 0, default: 0) - Stock mínimo para alertas
- `is_active`: bool (default: True) - Productos inactivos no se pueden vender
- `created_at`: datetime (auto)
- `updated_at`: datetime (auto, actualizado en cada cambio)
- `created_by`: UUID (FK -> User.id, nullable=False)

### Relaciones:
- `category`: Category | None (many-to-one, back_populates="products")
- `created_by_user`: User (many-to-one, back_populates="products")
- `inventory_movements`: List[InventoryMovement] (one-to-many, back_populates="product")
- `alerts`: List[Alert] (one-to-many, back_populates="product")

### Constraints:
- UNIQUE(sku)
- CHECK(current_stock >= 0)
- CHECK(min_stock >= 0)
- CHECK(unit_price > 0)
- CHECK(sale_price > 0)
- CHECK(LENGTH(sku) >= 1)
- CHECK(LENGTH(name) >= 1)

### Índices:
- PRIMARY KEY (id)
- UNIQUE INDEX (sku)
- INDEX (category_id)
- INDEX (created_by)
- INDEX (current_stock, min_stock) - Para consultas de alertas

### Lógica de negocio:
- Al crear: `current_stock = 0` por defecto
- Al actualizar `current_stock`: generar alerta si `current_stock <= min_stock`
- El `current_stock` SOLO se actualiza mediante InventoryMovement

---

## 4. InventoryMovement (NUEVA TABLA)

**Propósito:** Registro de todos los movimientos de inventario (Kardex)

### Campos:
- `id`: UUID (PK)
- `product_id`: UUID (FK -> Product.id, nullable=False, on_delete=RESTRICT)
- `movement_type`: Enum MovementType (ver tipos abajo)
- `quantity`: int (positivo para entradas, negativo para salidas)
- `reference_number`: str | None (max_length=100) - Factura, orden de compra, ticket
- `notes`: str | None (max_length=500) - Motivo del ajuste, observaciones
- `unit_price`: Decimal(10, 2) | None - Precio unitario en el momento (para compras)
- `total_amount`: Decimal(10, 2) | None - Monto total (quantity * unit_price)
- `stock_before`: int (>= 0) - Stock ANTES del movimiento
- `stock_after`: int (>= 0) - Stock DESPUÉS del movimiento
- `movement_date`: datetime - Fecha/hora del movimiento
- `created_at`: datetime (auto) - Fecha/hora de registro en sistema
- `created_by`: UUID (FK -> User.id, nullable=False)

### Tipos de movimiento (MovementType Enum):
```python
class MovementType(str, Enum):
    ENTRADA_COMPRA = "entrada_compra"           # Compra a proveedor (+ stock)
    SALIDA_VENTA = "salida_venta"               # Venta a cliente (- stock)
    AJUSTE_CONTEO = "ajuste_conteo"             # Ajuste por conteo físico (+/-)
    AJUSTE_MERMA = "ajuste_merma"               # Merma, robo, daño (- stock)
    DEVOLUCION_CLIENTE = "devolucion_cliente"   # Cliente devuelve (+ stock)
    DEVOLUCION_PROVEEDOR = "devolucion_proveedor" # Devolver a proveedor (- stock)
```

### Relaciones:
- `product`: Product (many-to-one, back_populates="inventory_movements")
- `created_by_user`: User (many-to-one, back_populates="inventory_movements")

### Constraints:
- CHECK(stock_before >= 0)
- CHECK(stock_after >= 0)
- CHECK(quantity != 0) - No se permiten movimientos de 0
- RESTRICT on DELETE product - Para mantener historial

### Índices:
- PRIMARY KEY (id)
- INDEX (product_id, movement_date DESC) - Para kardex
- INDEX (movement_type)
- INDEX (created_by)
- INDEX (movement_date DESC) - Para reportes por período

### Lógica de negocio:
1. Al crear movimiento:
   - Capturar `stock_before` = Product.current_stock
   - Calcular `stock_after` = stock_before + quantity (positivo o negativo según tipo)
   - Actualizar Product.current_stock = stock_after
   - Validar que stock_after >= 0 (no permitir stock negativo)
   - Si stock_after <= Product.min_stock: crear Alert
2. El campo `total_amount` se calcula: abs(quantity) * unit_price (si aplica)
3. El movimiento es INMUTABLE una vez creado (no se puede editar ni eliminar)

---

## 5. Alert (NUEVA TABLA)

**Propósito:** Alertas automáticas de stock bajo

### Campos:
- `id`: UUID (PK)
- `product_id`: UUID (FK -> Product.id, nullable=False, on_delete=CASCADE)
- `alert_type`: Enum AlertType ("low_stock", "out_of_stock")
- `current_stock`: int - Stock al momento de generar la alerta
- `min_stock`: int - Stock mínimo configurado del producto
- `is_resolved`: bool (default: False)
- `resolved_at`: datetime | None
- `resolved_by`: UUID | None (FK -> User.id, nullable=True)
- `notes`: str | None (max_length=500) - Notas sobre la resolución
- `created_at`: datetime (auto)

### Tipos de alerta (AlertType Enum):
```python
class AlertType(str, Enum):
    LOW_STOCK = "low_stock"       # 0 < current_stock <= min_stock
    OUT_OF_STOCK = "out_of_stock" # current_stock = 0
```

### Relaciones:
- `product`: Product (many-to-one, back_populates="alerts")
- `resolved_by_user`: User | None (many-to-one)

### Constraints:
- CHECK(current_stock >= 0)
- CHECK(min_stock >= 0)

### Índices:
- PRIMARY KEY (id)
- INDEX (product_id, is_resolved)
- INDEX (is_resolved, created_at DESC) - Para bandeja de alertas activas
- INDEX (alert_type)

### Lógica de negocio:
1. Generación automática al crear/actualizar InventoryMovement:
   - Si stock_after = 0: crear alerta tipo "out_of_stock"
   - Si 0 < stock_after <= min_stock: crear alerta tipo "low_stock"
   - No crear duplicados: verificar que no exista alerta no resuelta para el producto
2. Resolución manual o automática:
   - Manual: Administrador marca como resuelta con notas
   - Automática: Al registrar entrada que supere min_stock, resolver alerta existente

---

## Diagrama de Relaciones

```
User (extendido)
  |
  +-- categories (1:N) --> Category
  |                           |
  |                           +-- products (1:N) --> Product
  |                                                      |
  +-- products (1:N) ---------------------------------> |
  |                                                      |
  +-- inventory_movements (1:N) --> InventoryMovement --+
                                                         |
                                     Alert <-------------+
```

---

## Flujos de Datos Críticos

### 1. Registrar Entrada (Compra)
```
Usuario (Auxiliar) → POST /inventory-movements
  {
    "product_id": "uuid",
    "movement_type": "entrada_compra",
    "quantity": 50,
    "unit_price": 10.50,
    "reference_number": "FC-001",
    "notes": "Compra a Proveedor X"
  }

Backend:
  1. Obtener Product.current_stock → stock_before
  2. Calcular stock_after = stock_before + 50
  3. Crear InventoryMovement con stock_before y stock_after
  4. Actualizar Product.current_stock = stock_after
  5. Calcular total_amount = 50 * 10.50 = 525.00
  6. Si stock_after > min_stock y existe Alert no resuelta → resolver Alert
  7. Retornar movimiento creado con código 201
```

### 2. Registrar Salida (Venta)
```
Usuario (Vendedor) → POST /inventory-movements
  {
    "product_id": "uuid",
    "movement_type": "salida_venta",
    "quantity": -10,
    "reference_number": "VT-042",
    "notes": "Venta mostrador"
  }

Backend:
  1. Obtener Product.current_stock → stock_before
  2. Calcular stock_after = stock_before - 10
  3. VALIDAR: stock_after >= 0, si no → error 400 "Stock insuficiente"
  4. Crear InventoryMovement
  5. Actualizar Product.current_stock = stock_after
  6. Si stock_after <= min_stock → crear Alert
  7. Retornar movimiento creado
```

### 3. Consultar Kardex
```
Usuario → GET /kardex/{product_id}?start_date=2025-01-01&end_date=2025-01-31

Backend:
  1. Validar permisos (todos los usuarios autenticados)
  2. Filtrar InventoryMovement por product_id y rango de fechas
  3. Ordenar por movement_date DESC
  4. Retornar lista con:
     - Fecha, tipo, cantidad, stock_before, stock_after, usuario, referencia
  5. Incluir saldo final (último stock_after)
```

### 4. Generar Reporte de Inventario
```
Usuario (Administrador) → GET /reports/inventory?format=csv

Backend:
  1. Obtener todos los Products activos
  2. Calcular por cada producto:
     - current_stock
     - Valor en inventario = current_stock * unit_price
     - Estado = "OK" | "Bajo stock" | "Agotado"
  3. Generar CSV con columnas:
     SKU, Nombre, Categoría, Stock Actual, Stock Mínimo, Valor, Estado
  4. Retornar archivo CSV para descarga
```

---

## Requisitos de Rendimiento

- **R11. Actualización < 1 segundo:**
  - Usar transacciones atómicas para InventoryMovement + Product.update
  - Índices en campos de consulta frecuente
  - Evitar N+1 queries con `selectinload` en relaciones

- **Concurrencia:**
  - Bloqueo optimista o pesimista en Product.current_stock durante actualización
  - Usar `session.execute(select(Product).where(...).with_for_update())`

---

## Seguridad

- **R12. Autenticación y Autorización:**
  - JWT para autenticación (ya implementado)
  - Decoradores de permisos por rol:
    - `@require_role(["administrador"])` - Solo admin
    - `@require_role(["administrador", "vendedor"])` - Admin o vendedor
    - `@require_role(["administrador", "auxiliar"])` - Admin o auxiliar
  - HTTPS obligatorio en producción

- **Validaciones:**
  - SKU único a nivel DB y API
  - Stock nunca negativo
  - Precios siempre positivos
  - Movimientos inmutables (no DELETE ni UPDATE)

---

## Migraciones

Orden de creación de tablas (respetando FKs):

1. User (ya existe, solo agregar columna `role`)
2. Category
3. Product (FK a Category y User)
4. InventoryMovement (FK a Product y User)
5. Alert (FK a Product y User)

Script Alembic:
```bash
alembic revision --autogenerate -m "Add inventory management system tables"
alembic upgrade head
```

---

## Datos Iniciales (Seeds)

Crear en `initial_data.py`:

1. **Categorías por defecto:**
   - Electrónica
   - Alimentos
   - Bebidas
   - Limpieza
   - Otros

2. **Usuario Administrador por defecto:**
   - email: admin@inventario.com
   - role: "administrador"
   - is_superuser: True

3. **Productos de ejemplo (opcional):**
   - 5-10 productos básicos para testing

---

## Validaciones de Negocio

### Product:
- ✓ SKU único (constraint DB + validación API)
- ✓ current_stock >= 0
- ✓ min_stock >= 0
- ✓ unit_price > 0
- ✓ sale_price > 0
- ✓ sale_price >= unit_price (advertencia, no error)

### InventoryMovement:
- ✓ quantity != 0
- ✓ stock_after >= 0 (no permitir ventas con stock insuficiente)
- ✓ movement_type válido
- ✓ reference_number requerido para compras y ventas
- ✓ notes requerido para ajustes

### Alert:
- ✓ No duplicar alertas no resueltas para mismo producto
- ✓ Resolver automáticamente al reabastecer

---

Este esquema cumple con TODOS los requisitos funcionales (RF-01 a RF-07) y casos de uso (CU-01 a CU-07) especificados en el documento de requerimientos.
