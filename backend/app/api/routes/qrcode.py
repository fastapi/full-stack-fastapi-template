import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import HTMLResponse
from jinja2 import Template
from sqlmodel import Session, select

from app.api.deps import SessionDep, get_current_user, get_db
from app.models.qrcode import QRCode  # Ensure you have this import for your model
from app.models.user import UserBusiness
from app.schema.qrcode import (
    QRCodeCreate,
    QRCodeRead,
    QRCodeUpdate,
)

# Ensure you have these imports for your schemas
from app.util import (
    check_user_permission,
    delete_record,
    get_record_by_id,
    update_record,
)

router = APIRouter()


# Return all QR codes for a specific venue
@router.get("/venue/{venue_id}", response_model=list[QRCodeRead])
async def read_qrcode_by_venue(
    venue_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: UserBusiness = Depends(get_current_user),
):
    """
    Retrieve all QR codes associated with a specific venue.
    """
    qrcodes = (
        db.execute(select(QRCode).where(QRCode.venue_id == venue_id)).scalars().all()
    )
    # if qrcode is empty, raise an error
    if not qrcodes:
        raise HTTPException(status_code=404, detail="No QR codes found for this venue.")

    check_user_permission(db, current_user, venue_id)
    return [qr_code.to_read_schema() for qr_code in qrcodes]


# Get a specific QR code
@router.get("/{qr_code_id}", response_model=QRCodeRead)
async def read_qr_code(
    qr_code_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: UserBusiness = Depends(get_current_user),
):
    """
    Retrieve a specific QR code by ID.
    """
    qr_code_instance = get_record_by_id(db, QRCode, qr_code_id)
    check_user_permission(db, current_user, qr_code_instance.venue_id)
    assert isinstance(
        qr_code_instance, QRCode
    ), "The returned object is not of type QRCode"
    return qr_code_instance.to_read_schema()


# Create a new QR code
@router.post("/", response_model=QRCodeRead)
async def create_qr_code(
    qr_code: QRCodeCreate,
    db: Session = Depends(get_db),
    current_user: UserBusiness = Depends(get_current_user),
):
    """
    Create a new QR code.
    """
    check_user_permission(db, current_user, qr_code.venue_id)
    try:
        qr_code_instance = QRCode.from_create_schema(qr_code)
        db.add(qr_code_instance)  # Persist the new QR code
        db.commit()  # Commit the session
        return (
            qr_code_instance.to_read_schema()
        )  # Call the instance method to convert to QRCodeRead
    except Exception as e:
        db.rollback()  # Rollback the session in case of any error
        raise HTTPException(status_code=500, detail=str(e)) from e


# Patch a QR code for partial updates
@router.patch("/{qr_code_id}", response_model=QRCodeRead)
async def update_qr_code(
    qr_code_id: uuid.UUID,
    updated_qr_code: QRCodeUpdate,
    db: Session = Depends(get_db),
    current_user: UserBusiness = Depends(get_current_user),
):
    qr_code_instance = get_record_by_id(db, QRCode, qr_code_id)

    if not qr_code_instance:
        raise HTTPException(status_code=404, detail="QR code not found.")

    # Check user permission before updating the QR code for this venue
    check_user_permission(db, current_user, qr_code_instance.venue_id)

    updated_qr_code = update_record(db, qr_code_instance, updated_qr_code)
    assert isinstance(
        updated_qr_code, QRCode
    ), "The returned object is not of type QRCode"
    return updated_qr_code.to_read_schema()


# Delete a QR code
@router.delete("/qrcode/{qr_code_id}", response_model=None)
async def delete_qr_code(
    qr_code_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: UserBusiness = Depends(get_current_user),
):
    """
    Delete a QR code by ID.
    """
    qr_code_instance = get_record_by_id(db, QRCode, qr_code_id)

    if not qr_code_instance:
        raise HTTPException(status_code=404, detail="QR code not found.")

    check_user_permission(db, current_user, qr_code_instance.venue_id)
    return delete_record(db, qr_code_instance)


@router.get("/scan/{qr_id}", response_class=HTMLResponse)
async def scan_qr_code(qr_id: uuid.UUID, session: SessionDep):
    """
    Scan a QR code to determine its associated venue and redirect appropriately.
    """
    # Retrieve the QR code from the database
    qr_code_result = session.execute(
        select(QRCode).where(QRCode.id == qr_id)
    ).one_or_none()

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
    print("template_path:", template_path)
    try:
        template_str = template_path.read_text()
    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=500, detail="Landing page template not found."
        ) from exc

    # Use string.Template to replace placeholders in the HTML
    template = Template(template_str)
    html_content = template.render(venueId=venue_id, venueType=venue_type)
    return HTMLResponse(content=html_content)
