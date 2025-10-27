import uuid
from typing import Any
from datetime import datetime
from decimal import Decimal

from sqlmodel import Session, select
from fastapi import HTTPException

from app.core.security import get_password_hash, verify_password
from app.models import (
    Item,
    ItemCreate,
    User,
    UserCreate,
    UserUpdate,
    # Inventory models
    Category,
    CategoryCreate,
    CategoryUpdate,
    Product,
    ProductCreate,
    ProductUpdate,
    InventoryMovement,
    InventoryMovementCreate,
    Alert,
    AlertCreate,
    AlertUpdate,
    AlertType,
    MovementType,
)


def create_user(*, session: Session, user_create: UserCreate) -> User:
    db_obj = User.model_validate(
        user_create, update={"hashed_password": get_password_hash(user_create.password)}
    )
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


def update_user(*, session: Session, db_user: User, user_in: UserUpdate) -> Any:
    user_data = user_in.model_dump(exclude_unset=True)
    extra_data = {}
    if "password" in user_data:
        password = user_data["password"]
        hashed_password = get_password_hash(password)
        extra_data["hashed_password"] = hashed_password
    db_user.sqlmodel_update(user_data, update=extra_data)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


def get_user_by_email(*, session: Session, email: str) -> User | None:
    statement = select(User).where(User.email == email)
    session_user = session.exec(statement).first()
    return session_user


def authenticate(*, session: Session, email: str, password: str) -> User | None:
    db_user = get_user_by_email(session=session, email=email)
    if not db_user:
        return None
    if not verify_password(password, db_user.hashed_password):
        return None
    return db_user


def create_item(*, session: Session, item_in: ItemCreate, owner_id: uuid.UUID) -> Item:
    db_item = Item.model_validate(item_in, update={"owner_id": owner_id})
    session.add(db_item)
    session.commit()
    session.refresh(db_item)
    return db_item


# ============================================================================
# INVENTORY MANAGEMENT SYSTEM - CRUD FUNCTIONS
# ============================================================================

# Category CRUD
# ============================================================================


def create_category(
    *, session: Session, category_in: CategoryCreate, created_by: uuid.UUID
) -> Category:
    """Create a new category"""
    # Check if category name already exists
    existing = get_category_by_name(session=session, name=category_in.name)
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"Category with name '{category_in.name}' already exists",
        )

    db_category = Category.model_validate(
        category_in, update={"created_by": created_by}
    )
    session.add(db_category)
    session.commit()
    session.refresh(db_category)
    return db_category


def get_category_by_id(*, session: Session, category_id: uuid.UUID) -> Category | None:
    """Get category by ID"""
    return session.get(Category, category_id)


def get_category_by_name(*, session: Session, name: str) -> Category | None:
    """Get category by name"""
    statement = select(Category).where(Category.name == name)
    return session.exec(statement).first()


def update_category(
    *, session: Session, db_category: Category, category_in: CategoryUpdate
) -> Category:
    """Update a category"""
    # If name is being updated, check for uniqueness
    if category_in.name and category_in.name != db_category.name:
        existing = get_category_by_name(session=session, name=category_in.name)
        if existing:
            raise HTTPException(
                status_code=400,
                detail=f"Category with name '{category_in.name}' already exists",
            )

    category_data = category_in.model_dump(exclude_unset=True)
    category_data["updated_at"] = datetime.utcnow()
    db_category.sqlmodel_update(category_data)
    session.add(db_category)
    session.commit()
    session.refresh(db_category)
    return db_category


# Product CRUD
# ============================================================================


def create_product(
    *, session: Session, product_in: ProductCreate, created_by: uuid.UUID
) -> Product:
    """Create a new product"""
    # Check if SKU already exists
    existing = get_product_by_sku(session=session, sku=product_in.sku)
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"Product with SKU '{product_in.sku}' already exists",
        )

    # Validate category exists if provided
    if product_in.category_id:
        category = get_category_by_id(session=session, category_id=product_in.category_id)
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")

    db_product = Product.model_validate(
        product_in,
        update={"created_by": created_by, "current_stock": 0}
    )
    session.add(db_product)
    session.commit()
    session.refresh(db_product)
    return db_product


def get_product_by_id(*, session: Session, product_id: uuid.UUID) -> Product | None:
    """Get product by ID"""
    return session.get(Product, product_id)


def get_product_by_sku(*, session: Session, sku: str) -> Product | None:
    """Get product by SKU"""
    statement = select(Product).where(Product.sku == sku)
    return session.exec(statement).first()


def update_product(
    *, session: Session, db_product: Product, product_in: ProductUpdate
) -> Product:
    """Update a product"""
    # If SKU is being updated, check for uniqueness
    if product_in.sku and product_in.sku != db_product.sku:
        existing = get_product_by_sku(session=session, sku=product_in.sku)
        if existing:
            raise HTTPException(
                status_code=400,
                detail=f"Product with SKU '{product_in.sku}' already exists",
            )

    # Validate category exists if being updated
    if product_in.category_id:
        category = get_category_by_id(session=session, category_id=product_in.category_id)
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")

    product_data = product_in.model_dump(exclude_unset=True)
    product_data["updated_at"] = datetime.utcnow()

    # Check if min_stock is being updated and if we need to create/resolve alerts
    old_min_stock = db_product.min_stock
    new_min_stock = product_data.get("min_stock", old_min_stock)

    db_product.sqlmodel_update(product_data)
    session.add(db_product)
    session.commit()
    session.refresh(db_product)

    # If min_stock increased and current_stock is now below it, create alert
    if new_min_stock > old_min_stock and db_product.current_stock <= new_min_stock:
        check_and_create_alert(session=session, product=db_product)
    # If min_stock decreased and current_stock is now above it, resolve existing alerts
    elif new_min_stock < old_min_stock and db_product.current_stock > new_min_stock:
        resolve_alerts_for_product(session=session, product_id=db_product.id)

    return db_product


# InventoryMovement CRUD
# ============================================================================


def create_inventory_movement(
    *,
    session: Session,
    movement_in: InventoryMovementCreate,
    created_by: uuid.UUID
) -> InventoryMovement:
    """
    Create a new inventory movement and update product stock.
    This function handles the critical business logic:
    1. Validates product exists
    2. Captures stock_before
    3. Calculates stock_after
    4. Validates stock won't go negative
    5. Updates product.current_stock
    6. Creates/resolves alerts as needed
    7. Calculates total_amount
    """
    # Get product
    product = get_product_by_id(session=session, product_id=movement_in.product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Capture current stock
    stock_before = product.current_stock

    # Calculate new stock based on movement type and quantity
    # For sales/outputs, quantity should be negative
    # For purchases/inputs, quantity should be positive
    if movement_in.movement_type in [
        MovementType.ENTRADA_COMPRA,
        MovementType.DEVOLUCION_CLIENTE,
    ]:
        # Entries - quantity should be positive
        if movement_in.quantity < 0:
            raise HTTPException(
                status_code=400,
                detail=f"Quantity must be positive for {movement_in.movement_type.value}"
            )
        stock_after = stock_before + movement_in.quantity
    elif movement_in.movement_type in [
        MovementType.SALIDA_VENTA,
        MovementType.AJUSTE_MERMA,
        MovementType.DEVOLUCION_PROVEEDOR,
    ]:
        # Exits - quantity should be positive but we subtract
        if movement_in.quantity < 0:
            raise HTTPException(
                status_code=400,
                detail=f"Quantity must be positive for {movement_in.movement_type.value}"
            )
        stock_after = stock_before - movement_in.quantity
    else:  # AJUSTE_CONTEO can be positive or negative
        stock_after = stock_before + movement_in.quantity

    # Validate stock won't go negative
    if stock_after < 0:
        raise HTTPException(
            status_code=400,
            detail=f"Insufficient stock. Current: {stock_before}, Requested: {abs(movement_in.quantity)}"
        )

    # Calculate total_amount if unit_price provided
    total_amount = None
    if movement_in.unit_price:
        total_amount = Decimal(abs(movement_in.quantity)) * movement_in.unit_price

    # For sales, use product's sale_price if no unit_price provided
    if movement_in.movement_type == MovementType.SALIDA_VENTA and not movement_in.unit_price:
        total_amount = Decimal(movement_in.quantity) * product.sale_price

    # Create movement record
    db_movement = InventoryMovement.model_validate(
        movement_in,
        update={
            "created_by": created_by,
            "stock_before": stock_before,
            "stock_after": stock_after,
            "total_amount": total_amount,
        }
    )
    session.add(db_movement)

    # Update product stock
    product.current_stock = stock_after
    product.updated_at = datetime.utcnow()
    session.add(product)

    # Commit transaction
    session.commit()
    session.refresh(db_movement)
    session.refresh(product)

    # Check and create/resolve alerts
    if stock_after <= product.min_stock:
        check_and_create_alert(session=session, product=product)
    elif stock_before <= product.min_stock and stock_after > product.min_stock:
        # Stock was low but now it's above minimum, resolve alerts
        resolve_alerts_for_product(session=session, product_id=product.id)

    return db_movement


def get_inventory_movement_by_id(
    *, session: Session, movement_id: uuid.UUID
) -> InventoryMovement | None:
    """Get inventory movement by ID"""
    return session.get(InventoryMovement, movement_id)


def get_movements_by_product(
    *,
    session: Session,
    product_id: uuid.UUID,
    skip: int = 0,
    limit: int = 100,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
) -> list[InventoryMovement]:
    """Get inventory movements for a product (Kardex)"""
    statement = select(InventoryMovement).where(
        InventoryMovement.product_id == product_id
    )

    if start_date:
        statement = statement.where(InventoryMovement.movement_date >= start_date)
    if end_date:
        statement = statement.where(InventoryMovement.movement_date <= end_date)

    statement = statement.order_by(InventoryMovement.movement_date.desc())
    statement = statement.offset(skip).limit(limit)

    return list(session.exec(statement).all())


# Alert CRUD
# ============================================================================


def create_alert(
    *, session: Session, alert_in: AlertCreate
) -> Alert:
    """Create a new alert"""
    db_alert = Alert.model_validate(alert_in)
    session.add(db_alert)
    session.commit()
    session.refresh(db_alert)
    return db_alert


def get_alert_by_id(*, session: Session, alert_id: uuid.UUID) -> Alert | None:
    """Get alert by ID"""
    return session.get(Alert, alert_id)


def get_active_alerts_by_product(
    *, session: Session, product_id: uuid.UUID
) -> list[Alert]:
    """Get active (unresolved) alerts for a product"""
    statement = select(Alert).where(
        Alert.product_id == product_id,
        Alert.is_resolved == False
    )
    return list(session.exec(statement).all())


def resolve_alert(
    *,
    session: Session,
    db_alert: Alert,
    resolved_by: uuid.UUID,
    notes: str | None = None
) -> Alert:
    """Resolve an alert"""
    db_alert.is_resolved = True
    db_alert.resolved_at = datetime.utcnow()
    db_alert.resolved_by = resolved_by
    if notes:
        db_alert.notes = notes

    session.add(db_alert)
    session.commit()
    session.refresh(db_alert)
    return db_alert


def resolve_alerts_for_product(
    *, session: Session, product_id: uuid.UUID
) -> None:
    """Resolve all active alerts for a product (when stock is replenished)"""
    active_alerts = get_active_alerts_by_product(session=session, product_id=product_id)
    for alert in active_alerts:
        alert.is_resolved = True
        alert.resolved_at = datetime.utcnow()
        alert.notes = "Auto-resolved: stock replenished above minimum"
        session.add(alert)

    if active_alerts:
        session.commit()


def check_and_create_alert(*, session: Session, product: Product) -> None:
    """
    Check if product needs an alert and create it if necessary.
    Only creates alert if there isn't already an active one.
    """
    # Check if there's already an active alert for this product
    active_alerts = get_active_alerts_by_product(session=session, product_id=product.id)
    if active_alerts:
        return  # Don't create duplicate alerts

    # Determine alert type
    if product.current_stock == 0:
        alert_type = AlertType.OUT_OF_STOCK
    elif product.current_stock <= product.min_stock:
        alert_type = AlertType.LOW_STOCK
    else:
        return  # No alert needed

    # Create alert
    alert_in = AlertCreate(
        product_id=product.id,
        alert_type=alert_type,
        current_stock=product.current_stock,
        min_stock=product.min_stock,
        notes=f"Automatic alert: stock at {product.current_stock} (min: {product.min_stock})"
    )
    create_alert(session=session, alert_in=alert_in)
