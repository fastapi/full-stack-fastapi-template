import uuid
import csv
import io
from typing import Any
from datetime import datetime
from decimal import Decimal

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlmodel import func, select
from pydantic import BaseModel

from app.api.deps import CurrentUser, SessionDep
from app.models import (
    Product,
    InventoryMovement,
    MovementType,
    Category,
)

router = APIRouter(prefix="/reports", tags=["reports"])


class InventoryReportItem(BaseModel):
    """Item in inventory report"""
    sku: str
    name: str
    category_name: str | None
    current_stock: int
    min_stock: int
    unit_price: Decimal
    sale_price: Decimal
    total_value: Decimal  # current_stock * unit_price
    stock_status: str  # "OK", "Low Stock", "Out of Stock"
    unit_of_measure: str


class InventoryReport(BaseModel):
    """Full inventory report"""
    generated_at: datetime
    total_products: int
    total_value: Decimal
    low_stock_count: int
    out_of_stock_count: int
    items: list[InventoryReportItem]


class SalesReportItem(BaseModel):
    """Item in sales report"""
    product_sku: str
    product_name: str
    quantity_sold: int
    total_sales: Decimal
    movement_count: int


class SalesReport(BaseModel):
    """Sales report"""
    generated_at: datetime
    start_date: datetime | None
    end_date: datetime | None
    total_sales: Decimal
    total_items_sold: int
    total_transactions: int
    items: list[SalesReportItem]


class PurchasesReportItem(BaseModel):
    """Item in purchases report"""
    product_sku: str
    product_name: str
    quantity_purchased: int
    total_cost: Decimal
    movement_count: int


class PurchasesReport(BaseModel):
    """Purchases report"""
    generated_at: datetime
    start_date: datetime | None
    end_date: datetime | None
    total_purchases: Decimal
    total_items_purchased: int
    total_transactions: int
    items: list[PurchasesReportItem]


@router.get("/inventory", response_model=InventoryReport)
def get_inventory_report(
    session: SessionDep,
    current_user: CurrentUser,
    category_id: uuid.UUID | None = None,
    active_only: bool = True,
) -> Any:
    """
    Generate inventory report.
    Shows current stock levels, values, and status for all products.
    All authenticated users can view.
    """
    # Build query
    statement = select(Product)
    if active_only:
        statement = statement.where(Product.is_active == True)
    if category_id:
        statement = statement.where(Product.category_id == category_id)

    statement = statement.order_by(Product.name)
    products = session.exec(statement).all()

    # Calculate metrics
    items = []
    total_value = Decimal(0)
    low_stock_count = 0
    out_of_stock_count = 0

    for product in products:
        # Get category name
        category_name = None
        if product.category_id:
            category = session.get(Category, product.category_id)
            if category:
                category_name = category.name

        # Calculate value
        item_value = Decimal(product.current_stock) * product.unit_price
        total_value += item_value

        # Determine status
        if product.current_stock == 0:
            stock_status = "Out of Stock"
            out_of_stock_count += 1
        elif product.current_stock <= product.min_stock:
            stock_status = "Low Stock"
            low_stock_count += 1
        else:
            stock_status = "OK"

        items.append(InventoryReportItem(
            sku=product.sku,
            name=product.name,
            category_name=category_name,
            current_stock=product.current_stock,
            min_stock=product.min_stock,
            unit_price=product.unit_price,
            sale_price=product.sale_price,
            total_value=item_value,
            stock_status=stock_status,
            unit_of_measure=product.unit_of_measure
        ))

    return InventoryReport(
        generated_at=datetime.utcnow(),
        total_products=len(products),
        total_value=total_value,
        low_stock_count=low_stock_count,
        out_of_stock_count=out_of_stock_count,
        items=items
    )


@router.get("/inventory/csv")
def export_inventory_report_csv(
    session: SessionDep,
    current_user: CurrentUser,
    category_id: uuid.UUID | None = None,
    active_only: bool = True,
) -> StreamingResponse:
    """
    Export inventory report as CSV.
    All authenticated users can export.
    """
    # Generate report
    report = get_inventory_report(
        session=session,
        current_user=current_user,
        category_id=category_id,
        active_only=active_only
    )

    # Create CSV
    output = io.StringIO()
    writer = csv.writer(output)

    # Write header
    writer.writerow([
        "SKU",
        "Product Name",
        "Category",
        "Current Stock",
        "Min Stock",
        "Unit Price",
        "Sale Price",
        "Total Value",
        "Status",
        "Unit of Measure"
    ])

    # Write rows
    for item in report.items:
        writer.writerow([
            item.sku,
            item.name,
            item.category_name or "N/A",
            item.current_stock,
            item.min_stock,
            float(item.unit_price),
            float(item.sale_price),
            float(item.total_value),
            item.stock_status,
            item.unit_of_measure
        ])

    # Write summary
    writer.writerow([])
    writer.writerow(["SUMMARY"])
    writer.writerow(["Total Products", report.total_products])
    writer.writerow(["Total Value", float(report.total_value)])
    writer.writerow(["Low Stock Count", report.low_stock_count])
    writer.writerow(["Out of Stock Count", report.out_of_stock_count])
    writer.writerow(["Generated At", report.generated_at.isoformat()])

    # Prepare response
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=inventory_report_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"
        }
    )


@router.get("/sales", response_model=SalesReport)
def get_sales_report(
    session: SessionDep,
    current_user: CurrentUser,
    start_date: datetime | None = Query(None, description="Start date"),
    end_date: datetime | None = Query(None, description="End date"),
    category_id: uuid.UUID | None = None,
) -> Any:
    """
    Generate sales report.
    Shows products sold, quantities, and revenue for a period.
    All authenticated users can view.
    """
    # Build query for sales movements
    statement = select(InventoryMovement).where(
        InventoryMovement.movement_type == MovementType.SALIDA_VENTA
    )

    if start_date:
        statement = statement.where(InventoryMovement.movement_date >= start_date)
    if end_date:
        statement = statement.where(InventoryMovement.movement_date <= end_date)

    movements = session.exec(statement).all()

    # Group by product
    product_sales: dict[uuid.UUID, dict] = {}

    for movement in movements:
        product_id = movement.product_id
        if product_id not in product_sales:
            product_sales[product_id] = {
                "quantity": 0,
                "total": Decimal(0),
                "count": 0
            }

        product_sales[product_id]["quantity"] += abs(movement.quantity)
        if movement.total_amount:
            product_sales[product_id]["total"] += movement.total_amount
        product_sales[product_id]["count"] += 1

    # Filter by category if requested
    if category_id:
        filtered_product_sales = {}
        for product_id, data in product_sales.items():
            product = session.get(Product, product_id)
            if product and product.category_id == category_id:
                filtered_product_sales[product_id] = data
        product_sales = filtered_product_sales

    # Build report items
    items = []
    total_sales = Decimal(0)
    total_items_sold = 0
    total_transactions = 0

    for product_id, data in product_sales.items():
        product = session.get(Product, product_id)
        if not product:
            continue

        items.append(SalesReportItem(
            product_sku=product.sku,
            product_name=product.name,
            quantity_sold=data["quantity"],
            total_sales=data["total"],
            movement_count=data["count"]
        ))

        total_sales += data["total"]
        total_items_sold += data["quantity"]
        total_transactions += data["count"]

    # Sort by total sales descending
    items.sort(key=lambda x: x.total_sales, reverse=True)

    return SalesReport(
        generated_at=datetime.utcnow(),
        start_date=start_date,
        end_date=end_date,
        total_sales=total_sales,
        total_items_sold=total_items_sold,
        total_transactions=total_transactions,
        items=items
    )


@router.get("/sales/csv")
def export_sales_report_csv(
    session: SessionDep,
    current_user: CurrentUser,
    start_date: datetime | None = Query(None, description="Start date"),
    end_date: datetime | None = Query(None, description="End date"),
    category_id: uuid.UUID | None = None,
) -> StreamingResponse:
    """Export sales report as CSV"""
    report = get_sales_report(
        session=session,
        current_user=current_user,
        start_date=start_date,
        end_date=end_date,
        category_id=category_id
    )

    # Create CSV
    output = io.StringIO()
    writer = csv.writer(output)

    # Write header
    writer.writerow(["SKU", "Product Name", "Quantity Sold", "Total Sales", "Number of Transactions"])

    # Write rows
    for item in report.items:
        writer.writerow([
            item.product_sku,
            item.product_name,
            item.quantity_sold,
            float(item.total_sales),
            item.movement_count
        ])

    # Write summary
    writer.writerow([])
    writer.writerow(["SUMMARY"])
    writer.writerow(["Period Start", report.start_date.isoformat() if report.start_date else "N/A"])
    writer.writerow(["Period End", report.end_date.isoformat() if report.end_date else "N/A"])
    writer.writerow(["Total Sales", float(report.total_sales)])
    writer.writerow(["Total Items Sold", report.total_items_sold])
    writer.writerow(["Total Transactions", report.total_transactions])
    writer.writerow(["Generated At", report.generated_at.isoformat()])

    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=sales_report_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"
        }
    )


@router.get("/purchases", response_model=PurchasesReport)
def get_purchases_report(
    session: SessionDep,
    current_user: CurrentUser,
    start_date: datetime | None = Query(None, description="Start date"),
    end_date: datetime | None = Query(None, description="End date"),
    category_id: uuid.UUID | None = None,
) -> Any:
    """
    Generate purchases report.
    Shows products purchased, quantities, and costs for a period.
    All authenticated users can view.
    """
    # Build query for purchase movements
    statement = select(InventoryMovement).where(
        InventoryMovement.movement_type == MovementType.ENTRADA_COMPRA
    )

    if start_date:
        statement = statement.where(InventoryMovement.movement_date >= start_date)
    if end_date:
        statement = statement.where(InventoryMovement.movement_date <= end_date)

    movements = session.exec(statement).all()

    # Group by product
    product_purchases: dict[uuid.UUID, dict] = {}

    for movement in movements:
        product_id = movement.product_id
        if product_id not in product_purchases:
            product_purchases[product_id] = {
                "quantity": 0,
                "total": Decimal(0),
                "count": 0
            }

        product_purchases[product_id]["quantity"] += movement.quantity
        if movement.total_amount:
            product_purchases[product_id]["total"] += movement.total_amount
        product_purchases[product_id]["count"] += 1

    # Filter by category if requested
    if category_id:
        filtered_product_purchases = {}
        for product_id, data in product_purchases.items():
            product = session.get(Product, product_id)
            if product and product.category_id == category_id:
                filtered_product_purchases[product_id] = data
        product_purchases = filtered_product_purchases

    # Build report items
    items = []
    total_purchases = Decimal(0)
    total_items_purchased = 0
    total_transactions = 0

    for product_id, data in product_purchases.items():
        product = session.get(Product, product_id)
        if not product:
            continue

        items.append(PurchasesReportItem(
            product_sku=product.sku,
            product_name=product.name,
            quantity_purchased=data["quantity"],
            total_cost=data["total"],
            movement_count=data["count"]
        ))

        total_purchases += data["total"]
        total_items_purchased += data["quantity"]
        total_transactions += data["count"]

    # Sort by total cost descending
    items.sort(key=lambda x: x.total_cost, reverse=True)

    return PurchasesReport(
        generated_at=datetime.utcnow(),
        start_date=start_date,
        end_date=end_date,
        total_purchases=total_purchases,
        total_items_purchased=total_items_purchased,
        total_transactions=total_transactions,
        items=items
    )


@router.get("/purchases/csv")
def export_purchases_report_csv(
    session: SessionDep,
    current_user: CurrentUser,
    start_date: datetime | None = Query(None, description="Start date"),
    end_date: datetime | None = Query(None, description="End date"),
    category_id: uuid.UUID | None = None,
) -> StreamingResponse:
    """Export purchases report as CSV"""
    report = get_purchases_report(
        session=session,
        current_user=current_user,
        start_date=start_date,
        end_date=end_date,
        category_id=category_id
    )

    # Create CSV
    output = io.StringIO()
    writer = csv.writer(output)

    # Write header
    writer.writerow(["SKU", "Product Name", "Quantity Purchased", "Total Cost", "Number of Transactions"])

    # Write rows
    for item in report.items:
        writer.writerow([
            item.product_sku,
            item.product_name,
            item.quantity_purchased,
            float(item.total_cost),
            item.movement_count
        ])

    # Write summary
    writer.writerow([])
    writer.writerow(["SUMMARY"])
    writer.writerow(["Period Start", report.start_date.isoformat() if report.start_date else "N/A"])
    writer.writerow(["Period End", report.end_date.isoformat() if report.end_date else "N/A"])
    writer.writerow(["Total Purchases", float(report.total_purchases)])
    writer.writerow(["Total Items Purchased", report.total_items_purchased])
    writer.writerow(["Total Transactions", report.total_transactions])
    writer.writerow(["Generated At", report.generated_at.isoformat()])

    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=purchases_report_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"
        }
    )
