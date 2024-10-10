from pathlib import Path
import uuid
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from jinja2 import Template
from sqlalchemy import UUID
from sqlmodel import select
from typing import List
from app.api.deps import SessionDep
from app.models.qrcode import QRCode  # Ensure you have this import for your model
from app.schema.qrcode import QRCodeCreate, QRCodeRead  # Ensure you have these imports for your schemas
from app.crud import (
    get_all_records,
    get_record_by_id,
    create_record,
    update_record,
    patch_record,
    delete_record
)

router = APIRouter()

# Get all QR codes
@router.get("/qr_codes/", response_model=List[QRCodeRead])
async def read_qr_codes(session: SessionDep):
    # Retrieve all QR codes
    return get_all_records(session, QRCode)

# Get a specific QR code
@router.get("/qr_codes/{qr_code_id}", response_model=QRCodeRead)
async def read_qr_code(qr_code_id: uuid.UUID, session: SessionDep):
    """
    Retrieve a specific QR code by ID.
    """
    return get_record_by_id(session, QRCode, qr_code_id)

# Create a new QR code
@router.post("/qr_codes/", response_model=QRCodeRead)
async def create_qr_code(qr_code: QRCodeCreate, session: SessionDep):
    """
    Create a new QR code.
    """
    return create_record(session, QRCode, qr_code)

# Update a QR code
@router.put("/qr_codes/{qr_code_id}", response_model=QRCodeRead)
async def update_qr_code(qr_code_id: uuid.UUID, updated_qr_code: QRCodeCreate, session: SessionDep):
    """
    Update an existing QR code.
    """
    return update_record(session, QRCode, qr_code_id, updated_qr_code)

# PATCH a QR code for partial updates
@router.patch("/qr_codes/{qr_code_id}", response_model=QRCodeRead)
async def patch_qr_code(qr_code_id: uuid.UUID, updated_qr_code: QRCodeCreate, session: SessionDep):
    """
    Partially update an existing QR code.
    """
    return patch_record(session, QRCode, qr_code_id, updated_qr_code)

# Delete a QR code
@router.delete("/qr_codes/{qr_code_id}", response_model=None)
async def delete_qr_code(qr_code_id: uuid.UUID, session: SessionDep):
    """
    Delete a QR code by ID.
    """
    return delete_record(session, QRCode, qr_code_id)

@router.get("/scan/{qr_id}", response_class=HTMLResponse)
async def scan_qr_code(qr_id: uuid.UUID, session: SessionDep):
    """
    Scan a QR code to determine its associated venue and redirect appropriately.
    """
    # Retrieve the QR code from the database
    qr_code_result = session.execute(select(QRCode).where(QRCode.id == qr_id)).one_or_none()
    
    if not qr_code_result:
        raise HTTPException(status_code=404, detail="QR code not found.")
    
    qr_code = qr_code_result[0]
    # Determine the venue type and ID from the QR code
    venue_type, venue_id = None, None

    if qr_code.foodcourt_id:
        venue_type = "foodcourt"
        venue_id = qr_code.foodcourt_id
    elif qr_code.qsr_id:
        venue_type = "qsr"
        venue_id = qr_code.qsr_id
    elif qr_code.nightclub_id:
        venue_type = "nightclub"
        venue_id = qr_code.nightclub_id
    elif qr_code.restaurant_id:
        venue_type = "restaurant"
        venue_id = qr_code.restaurant_id

    if not venue_type or not venue_id:
        raise HTTPException(status_code=400, detail="No associated venue found.")

    # Load the landing page HTML template
    template_path = Path(__file__).parent.parent.parent / "static" / "landing_page.html"
    print('template_path:', template_path)
    try:
        template_str = template_path.read_text()
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="Landing page template not found.")

    # Use string.Template to replace placeholders in the HTML
    template = Template(template_str)
    html_content = template.render(venueId=venue_id, venueType=venue_type)
    return HTMLResponse(content=html_content)