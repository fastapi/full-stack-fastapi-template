import uuid
from typing import Any

from fastapi import APIRouter, HTTPException, Query
from sqlmodel import func, select, or_

from app.api.deps import AdministradorUser, CurrentUser, SessionDep
from app import crud
from app.models import (
    Product,
    ProductCreate,
    ProductPublic,
    ProductsPublic,
    ProductUpdate,
    Message,
)

router = APIRouter(prefix="/products", tags=["products"])


@router.get("/", response_model=ProductsPublic)
def read_products(
    session: SessionDep,
    current_user: CurrentUser,
    skip: int = 0,
    limit: int = 100,
    active_only: bool = True,
    category_id: uuid.UUID | None = None,
    search: str | None = Query(None, description="Search by SKU or name"),
    low_stock_only: bool = False
) -> Any:
    """
    Retrieve products.
    All authenticated users can view products.
    Filters: active_only, category_id, search (SKU or name), low_stock_only
    """
    count_statement = select(func.count()).select_from(Product)
    statement = select(Product)

    # Filter by active status
    if active_only:
        count_statement = count_statement.where(Product.is_active == True)
        statement = statement.where(Product.is_active == True)

    # Filter by category
    if category_id:
        count_statement = count_statement.where(Product.category_id == category_id)
        statement = statement.where(Product.category_id == category_id)

    # Search by SKU or name
    if search:
        search_filter = or_(
            Product.sku.ilike(f"%{search}%"),
            Product.name.ilike(f"%{search}%")
        )
        count_statement = count_statement.where(search_filter)
        statement = statement.where(search_filter)

    # Filter by low stock
    if low_stock_only:
        low_stock_filter = Product.current_stock <= Product.min_stock
        count_statement = count_statement.where(low_stock_filter)
        statement = statement.where(low_stock_filter)

    count = session.exec(count_statement).one()
    statement = statement.offset(skip).limit(limit).order_by(Product.name)
    products = session.exec(statement).all()

    return ProductsPublic(data=products, count=count)


@router.get("/{id}", response_model=ProductPublic)
def read_product(
    session: SessionDep, current_user: CurrentUser, id: uuid.UUID
) -> Any:
    """
    Get product by ID.
    All authenticated users can view products.
    """
    product = crud.get_product_by_id(session=session, product_id=id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.get("/sku/{sku}", response_model=ProductPublic)
def read_product_by_sku(
    session: SessionDep, current_user: CurrentUser, sku: str
) -> Any:
    """
    Get product by SKU.
    All authenticated users can view products.
    """
    product = crud.get_product_by_sku(session=session, sku=sku)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.post("/", response_model=ProductPublic, status_code=201)
def create_product(
    *,
    session: SessionDep,
    current_user: AdministradorUser,
    product_in: ProductCreate
) -> Any:
    """
    Create new product.
    Only administrador can create products.
    SKU must be unique.
    """
    product = crud.create_product(
        session=session,
        product_in=product_in,
        created_by=current_user.id
    )
    return product


@router.patch("/{id}", response_model=ProductPublic)
def update_product(
    *,
    session: SessionDep,
    current_user: AdministradorUser,
    id: uuid.UUID,
    product_in: ProductUpdate,
) -> Any:
    """
    Update a product.
    Only administrador can update products.
    Note: current_stock should only be updated via inventory movements.
    """
    db_product = crud.get_product_by_id(session=session, product_id=id)
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")

    product = crud.update_product(
        session=session,
        db_product=db_product,
        product_in=product_in
    )
    return product


@router.delete("/{id}", response_model=Message)
def delete_product(
    session: SessionDep, current_user: AdministradorUser, id: uuid.UUID
) -> Any:
    """
    Soft delete a product (set is_active=False).
    Only administrador can delete products.
    """
    db_product = crud.get_product_by_id(session=session, product_id=id)
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Soft delete by setting is_active=False
    product_update = ProductUpdate(is_active=False)
    crud.update_product(
        session=session,
        db_product=db_product,
        product_in=product_update
    )

    return Message(message="Product deleted successfully")
