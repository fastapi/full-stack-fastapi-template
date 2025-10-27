import uuid
from typing import Any
from datetime import datetime

from fastapi import APIRouter, HTTPException, Query
from sqlmodel import func, select

from app.api.deps import CurrentUser, SessionDep
from app import crud
from app.models import (
    InventoryMovement,
    InventoryMovementPublic,
    InventoryMovementsPublic,
    Product,
    ProductPublic,
)
from pydantic import BaseModel


class KardexReport(BaseModel):
    """Kardex report with product info and movements"""
    product: ProductPublic
    movements: list[InventoryMovementPublic]
    total_movements: int
    current_stock: int
    stock_status: str  # "OK", "Low Stock", "Out of Stock"


router = APIRouter(prefix="/kardex", tags=["kardex"])


@router.get("/{product_id}", response_model=KardexReport)
def get_kardex(
    session: SessionDep,
    current_user: CurrentUser,
    product_id: uuid.UUID,
    start_date: datetime | None = Query(None, description="Start date for filtering movements"),
    end_date: datetime | None = Query(None, description="End date for filtering movements"),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Get Kardex (movement history) for a product.
    All authenticated users can view kardex.

    Returns:
    - Product information
    - List of movements (filtered by date if provided)
    - Total number of movements
    - Current stock
    - Stock status
    """
    # Get product
    product = crud.get_product_by_id(session=session, product_id=product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Get movements
    movements = crud.get_movements_by_product(
        session=session,
        product_id=product_id,
        skip=skip,
        limit=limit,
        start_date=start_date,
        end_date=end_date
    )

    # Get total count of movements
    count_statement = select(func.count()).select_from(InventoryMovement).where(
        InventoryMovement.product_id == product_id
    )
    if start_date:
        count_statement = count_statement.where(InventoryMovement.movement_date >= start_date)
    if end_date:
        count_statement = count_statement.where(InventoryMovement.movement_date <= end_date)

    total_movements = session.exec(count_statement).one()

    # Determine stock status
    if product.current_stock == 0:
        stock_status = "Out of Stock"
    elif product.current_stock <= product.min_stock:
        stock_status = "Low Stock"
    else:
        stock_status = "OK"

    return KardexReport(
        product=ProductPublic.model_validate(product),
        movements=[InventoryMovementPublic.model_validate(m) for m in movements],
        total_movements=total_movements,
        current_stock=product.current_stock,
        stock_status=stock_status
    )


@router.get("/sku/{sku}", response_model=KardexReport)
def get_kardex_by_sku(
    session: SessionDep,
    current_user: CurrentUser,
    sku: str,
    start_date: datetime | None = Query(None, description="Start date for filtering movements"),
    end_date: datetime | None = Query(None, description="End date for filtering movements"),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Get Kardex by product SKU instead of ID.
    Convenient endpoint for barcode scanning integration.
    """
    # Get product by SKU
    product = crud.get_product_by_sku(session=session, sku=sku)
    if not product:
        raise HTTPException(status_code=404, detail=f"Product with SKU '{sku}' not found")

    # Reuse the main kardex endpoint logic
    return get_kardex(
        session=session,
        current_user=current_user,
        product_id=product.id,
        start_date=start_date,
        end_date=end_date,
        skip=skip,
        limit=limit
    )
