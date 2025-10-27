import uuid
from typing import Any
from datetime import datetime

from fastapi import APIRouter, HTTPException, Query
from sqlmodel import func, select

from app.api.deps import (
    AdministradorOrAuxiliarUser,
    AdministradorOrVendedorUser,
    AdministradorUser,
    CurrentUser,
    SessionDep,
)
from app import crud
from app.models import (
    InventoryMovement,
    InventoryMovementCreate,
    InventoryMovementPublic,
    InventoryMovementsPublic,
    MovementType,
    Message,
    UserRole,
)

router = APIRouter(prefix="/inventory-movements", tags=["inventory-movements"])


@router.get("/", response_model=InventoryMovementsPublic)
def read_inventory_movements(
    session: SessionDep,
    current_user: CurrentUser,
    skip: int = 0,
    limit: int = 100,
    product_id: uuid.UUID | None = None,
    movement_type: MovementType | None = None,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
) -> Any:
    """
    Retrieve inventory movements.
    All authenticated users can view movements.
    Filters: product_id, movement_type, date range
    """
    count_statement = select(func.count()).select_from(InventoryMovement)
    statement = select(InventoryMovement)

    # Filter by product
    if product_id:
        count_statement = count_statement.where(InventoryMovement.product_id == product_id)
        statement = statement.where(InventoryMovement.product_id == product_id)

    # Filter by movement type
    if movement_type:
        count_statement = count_statement.where(InventoryMovement.movement_type == movement_type)
        statement = statement.where(InventoryMovement.movement_type == movement_type)

    # Filter by date range
    if start_date:
        count_statement = count_statement.where(InventoryMovement.movement_date >= start_date)
        statement = statement.where(InventoryMovement.movement_date >= start_date)
    if end_date:
        count_statement = count_statement.where(InventoryMovement.movement_date <= end_date)
        statement = statement.where(InventoryMovement.movement_date <= end_date)

    count = session.exec(count_statement).one()
    statement = statement.offset(skip).limit(limit).order_by(InventoryMovement.movement_date.desc())
    movements = session.exec(statement).all()

    return InventoryMovementsPublic(data=movements, count=count)


@router.get("/{id}", response_model=InventoryMovementPublic)
def read_inventory_movement(
    session: SessionDep, current_user: CurrentUser, id: uuid.UUID
) -> Any:
    """
    Get inventory movement by ID.
    All authenticated users can view movements.
    """
    movement = crud.get_inventory_movement_by_id(session=session, movement_id=id)
    if not movement:
        raise HTTPException(status_code=404, detail="Inventory movement not found")
    return movement


@router.post("/entrada", response_model=InventoryMovementPublic, status_code=201)
def create_entrada(
    *,
    session: SessionDep,
    current_user: AdministradorOrAuxiliarUser,
    movement_in: InventoryMovementCreate
) -> Any:
    """
    Create new entrada (purchase/receipt).
    Only administrador or auxiliar can create entradas.
    Automatically updates product stock and resolves alerts if needed.
    """
    # Validate movement type
    if movement_in.movement_type not in [
        MovementType.ENTRADA_COMPRA,
        MovementType.DEVOLUCION_CLIENTE
    ]:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid movement type for entrada. Use: {MovementType.ENTRADA_COMPRA.value} or {MovementType.DEVOLUCION_CLIENTE.value}"
        )

    # Validate required fields for purchases
    if movement_in.movement_type == MovementType.ENTRADA_COMPRA:
        if not movement_in.reference_number:
            raise HTTPException(
                status_code=400,
                detail="reference_number is required for purchases"
            )
        if not movement_in.unit_price:
            raise HTTPException(
                status_code=400,
                detail="unit_price is required for purchases"
            )

    movement = crud.create_inventory_movement(
        session=session,
        movement_in=movement_in,
        created_by=current_user.id
    )
    return movement


@router.post("/salida", response_model=InventoryMovementPublic, status_code=201)
def create_salida(
    *,
    session: SessionDep,
    current_user: AdministradorOrVendedorUser,
    movement_in: InventoryMovementCreate
) -> Any:
    """
    Create new salida (sale).
    Only administrador or vendedor can create salidas.
    Automatically updates product stock and creates alerts if needed.
    """
    # Validate movement type
    if movement_in.movement_type != MovementType.SALIDA_VENTA:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid movement type for salida. Use: {MovementType.SALIDA_VENTA.value}"
        )

    # Validate required fields for sales
    if not movement_in.reference_number:
        raise HTTPException(
            status_code=400,
            detail="reference_number is required for sales"
        )

    movement = crud.create_inventory_movement(
        session=session,
        movement_in=movement_in,
        created_by=current_user.id
    )
    return movement


@router.post("/ajuste", response_model=InventoryMovementPublic, status_code=201)
def create_ajuste(
    *,
    session: SessionDep,
    current_user: AdministradorOrAuxiliarUser,
    movement_in: InventoryMovementCreate
) -> Any:
    """
    Create new ajuste (adjustment for count/shrinkage).
    Only administrador or auxiliar can create ajustes.
    Automatically updates product stock and manages alerts.
    """
    # Validate movement type
    if movement_in.movement_type not in [
        MovementType.AJUSTE_CONTEO,
        MovementType.AJUSTE_MERMA,
        MovementType.DEVOLUCION_PROVEEDOR
    ]:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid movement type for ajuste. Use: {MovementType.AJUSTE_CONTEO.value}, {MovementType.AJUSTE_MERMA.value}, or {MovementType.DEVOLUCION_PROVEEDOR.value}"
        )

    # Validate required fields for adjustments
    if not movement_in.notes:
        raise HTTPException(
            status_code=400,
            detail="notes field is required for adjustments (must explain reason)"
        )

    movement = crud.create_inventory_movement(
        session=session,
        movement_in=movement_in,
        created_by=current_user.id
    )
    return movement


@router.post("/", response_model=InventoryMovementPublic, status_code=201)
def create_inventory_movement(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    movement_in: InventoryMovementCreate
) -> Any:
    """
    Create new inventory movement (generic endpoint).
    Role-based access:
    - Entradas (compras/devoluciones cliente): Administrador or Auxiliar
    - Salidas (ventas): Administrador or Vendedor
    - Ajustes: Administrador or Auxiliar

    This endpoint validates role permissions based on movement type.
    """
    # Role-based validation
    if movement_in.movement_type in [
        MovementType.ENTRADA_COMPRA,
        MovementType.DEVOLUCION_CLIENTE,
        MovementType.AJUSTE_CONTEO,
        MovementType.AJUSTE_MERMA,
        MovementType.DEVOLUCION_PROVEEDOR
    ]:
        # Requires administrador or auxiliar
        if not current_user.is_superuser and current_user.role not in [
            UserRole.ADMINISTRADOR,
            UserRole.AUXILIAR
        ]:
            raise HTTPException(
                status_code=403,
                detail="Access denied. Administrador or Auxiliar role required for this movement type."
            )
    elif movement_in.movement_type == MovementType.SALIDA_VENTA:
        # Requires administrador or vendedor
        if not current_user.is_superuser and current_user.role not in [
            UserRole.ADMINISTRADOR,
            UserRole.VENDEDOR
        ]:
            raise HTTPException(
                status_code=403,
                detail="Access denied. Administrador or Vendedor role required for sales."
            )

    # Validate required fields based on movement type
    if movement_in.movement_type in [MovementType.ENTRADA_COMPRA, MovementType.SALIDA_VENTA]:
        if not movement_in.reference_number:
            raise HTTPException(
                status_code=400,
                detail="reference_number is required for purchases and sales"
            )

    if movement_in.movement_type in [
        MovementType.AJUSTE_CONTEO,
        MovementType.AJUSTE_MERMA
    ]:
        if not movement_in.notes:
            raise HTTPException(
                status_code=400,
                detail="notes field is required for adjustments"
            )

    if movement_in.movement_type == MovementType.ENTRADA_COMPRA and not movement_in.unit_price:
        raise HTTPException(
            status_code=400,
            detail="unit_price is required for purchases"
        )

    movement = crud.create_inventory_movement(
        session=session,
        movement_in=movement_in,
        created_by=current_user.id
    )
    return movement
