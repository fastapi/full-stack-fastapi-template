"""Payment API routes for Razorpay integration."""

import uuid
from typing import Any

from fastapi import APIRouter, HTTPException, Request, status
from fastapi.responses import JSONResponse

from app.api.deps import CurrentUser, SessionDep
from app.core.config import settings
from app.crud import (
    create_order as crud_create_order,
    create_payment,
    get_order_by_id,
    get_order_by_razorpay_id,
    get_payments_by_order,
    get_user_orders,
    update_order_status,
)
from app.models import (
    Message,
    OrderCreate,
    OrderCreateRequest,
    OrderCreateResponse,
    OrderPublic,
    OrdersPublic,
    PaymentCreate,
    PaymentPublic,
    PaymentVerifyRequest,
    PaymentVerifyResponse,
)
from app.services.razorpay_service import RazorpayClient, get_razorpay_client

router = APIRouter(prefix="/payments", tags=["payments"])


@router.post("/create-order", response_model=OrderCreateResponse, status_code=status.HTTP_201_CREATED)
def create_order(
    *, session: SessionDep, current_user: CurrentUser, order_in: OrderCreateRequest
) -> Any:
    """
    Create a Razorpay order for payment.

    This endpoint creates an order on Razorpay and saves it to the database.
    Returns order details including Razorpay Key ID for frontend integration.
    """
    if not settings.razorpay_enabled:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Payment service is not configured. Please set RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET.",
        )

    try:
        # Create Razorpay order
        razorpay_client = get_razorpay_client()
        razorpay_order = razorpay_client.create_order(
            amount=order_in.amount,
            currency=order_in.currency,
            receipt=order_in.receipt,
            notes=order_in.notes,
        )

        # Save order to database
        order_create = OrderCreate(
            amount=order_in.amount,
            currency=order_in.currency,
            receipt=order_in.receipt,
            notes=order_in.notes,
        )
        crud_create_order(
            session=session,
            order_in=order_create,
            user_id=current_user.id,
            razorpay_order_id=razorpay_order["id"],
        )

        # Return response with Razorpay key for frontend
        return OrderCreateResponse(
            id=razorpay_order["id"],
            order_id=razorpay_order["id"],
            amount=razorpay_order["amount"],
            currency=razorpay_order["currency"],
            key=settings.RAZORPAY_KEY_ID,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create order: {str(e)}",
        ) from e


@router.post("/verify", response_model=PaymentVerifyResponse)
def verify_payment(
    *, session: SessionDep, current_user: CurrentUser, payment_in: PaymentVerifyRequest
) -> Any:
    """
    Verify payment signature and save payment record.

    After Razorpay checkout, this endpoint verifies the payment signature
    and creates a payment record in the database.
    """
    if not settings.razorpay_enabled:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Payment service is not configured.",
        )

    try:
        # Get order from database
        order = get_order_by_razorpay_id(
            session=session, razorpay_order_id=payment_in.razorpay_order_id
        )
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found",
            )

        # Verify user owns the order
        if order.user_id != current_user.id and not current_user.is_superuser:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions",
            )

        # Verify payment signature
        razorpay_client = get_razorpay_client()
        is_valid = razorpay_client.verify_payment_signature(
            order_id=payment_in.razorpay_order_id,
            payment_id=payment_in.razorpay_payment_id,
            signature=payment_in.razorpay_signature,
        )

        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid payment signature",
            )

        # Get payment details from Razorpay
        razorpay_order_data = razorpay_client.get_order(payment_in.razorpay_order_id)
        payment_amount = int(razorpay_order_data.get("amount", order.amount))
        payment_currency = razorpay_order_data.get("currency", order.currency)

        # Create or update payment record
        payment_create = PaymentCreate(
            order_id=order.id,
            razorpay_payment_id=payment_in.razorpay_payment_id,
            razorpay_signature=payment_in.razorpay_signature,
            amount=payment_amount,
            currency=payment_currency,
            method=None,  # Can be updated from webhook
            status="captured",
        )
        payment = create_payment(session=session, payment_in=payment_create)

        # Update order status
        update_order_status(session=session, order=order, status="paid")

        return PaymentVerifyResponse(
            success=True,
            order=OrderPublic.model_validate(order),
            payment=PaymentPublic.model_validate(payment),
        )
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to verify payment: {str(e)}",
        ) from e


@router.post("/webhook")
async def webhook_handler(request: Request, session: SessionDep) -> JSONResponse:
    """
    Handle Razorpay webhook events.

    This endpoint receives webhook notifications from Razorpay
    and updates payment and order status accordingly.
    """
    if not settings.razorpay_enabled:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"message": "Payment service is not configured"},
        )

    try:
        # Get webhook payload
        payload_bytes = await request.body()
        payload_str = payload_bytes.decode("utf-8")
        webhook_data = await request.json()

        # Get signature from headers
        signature = request.headers.get("X-Razorpay-Signature")
        if not signature:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"message": "Missing webhook signature"},
            )

        # Verify webhook signature
        razorpay_client = get_razorpay_client()
        is_valid = razorpay_client.verify_webhook_signature(payload_str, signature)

        if not is_valid:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"message": "Invalid webhook signature"},
            )

        # Process webhook event
        event = webhook_data.get("event")
        payload = webhook_data.get("payload", {})

        if event == "payment.authorized":
            payment_data = payload.get("payment", {}).get("entity", {})
            order_data = payload.get("order", {}).get("entity", {})

            # Find order
            razorpay_order_id = order_data.get("id")
            if razorpay_order_id:
                order = get_order_by_razorpay_id(
                    session=session, razorpay_order_id=razorpay_order_id
                )
                if order:
                    # Create or update payment
                    payment_id = payment_data.get("id")
                    if payment_id:
                        existing_payments = get_payments_by_order(
                            session=session, order_id=order.id
                        )
                        existing_payment = next(
                            (p for p in existing_payments if p.razorpay_payment_id == payment_id),
                            None,
                        )

                        if not existing_payment:
                            payment_create = PaymentCreate(
                                order_id=order.id,
                                razorpay_payment_id=payment_id,
                                razorpay_signature=None,
                                amount=int(payment_data.get("amount", 0)),
                                currency=payment_data.get("currency", "INR"),
                                method=payment_data.get("method"),
                                status="authorized",
                            )
                            create_payment(session=session, payment_in=payment_create)

        elif event == "payment.captured":
            payment_data = payload.get("payment", {}).get("entity", {})
            order_data = payload.get("order", {}).get("entity", {})

            razorpay_order_id = order_data.get("id")
            payment_id = payment_data.get("id")

            if razorpay_order_id and payment_id:
                order = get_order_by_razorpay_id(
                    session=session, razorpay_order_id=razorpay_order_id
                )
                if order:
                    # Update order status
                    update_order_status(session=session, order=order, status="paid")

                    # Update or create payment
                    existing_payments = get_payments_by_order(
                        session=session, order_id=order.id
                    )
                    existing_payment = next(
                        (p for p in existing_payments if p.razorpay_payment_id == payment_id),
                        None,
                    )

                    if existing_payment:
                        existing_payment.status = "captured"
                        existing_payment.method = payment_data.get("method")
                        session.add(existing_payment)
                        session.commit()
                    else:
                        payment_create = PaymentCreate(
                            order_id=order.id,
                            razorpay_payment_id=payment_id,
                            razorpay_signature=None,
                            amount=int(payment_data.get("amount", 0)),
                            currency=payment_data.get("currency", "INR"),
                            method=payment_data.get("method"),
                            status="captured",
                        )
                        create_payment(session=session, payment_in=payment_create)

        elif event == "payment.failed":
            payment_data = payload.get("payment", {}).get("entity", {})
            order_data = payload.get("order", {}).get("entity", {})

            razorpay_order_id = order_data.get("id")
            payment_id = payment_data.get("id")

            if razorpay_order_id and payment_id:
                order = get_order_by_razorpay_id(
                    session=session, razorpay_order_id=razorpay_order_id
                )
                if order:
                    # Update order status
                    update_order_status(session=session, order=order, status="failed")

                    # Update or create payment
                    existing_payments = get_payments_by_order(
                        session=session, order_id=order.id
                    )
                    existing_payment = next(
                        (p for p in existing_payments if p.razorpay_payment_id == payment_id),
                        None,
                    )

                    if existing_payment:
                        existing_payment.status = "failed"
                        session.add(existing_payment)
                        session.commit()
                    else:
                        payment_create = PaymentCreate(
                            order_id=order.id,
                            razorpay_payment_id=payment_id,
                            razorpay_signature=None,
                            amount=int(payment_data.get("amount", 0)),
                            currency=payment_data.get("currency", "INR"),
                            method=payment_data.get("method"),
                            status="failed",
                        )
                        create_payment(session=session, payment_in=payment_create)

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"message": "Webhook processed successfully"},
        )
    except Exception as e:
        # Log error but return 200 to prevent Razorpay from retrying
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"message": f"Webhook processing error: {str(e)}"},
        )


@router.get("/orders", response_model=OrdersPublic)
def read_orders(
    session: SessionDep, current_user: CurrentUser, skip: int = 0, limit: int = 100
) -> Any:
    """
    Retrieve paginated list of orders for the current user.
    """
    orders, count = get_user_orders(
        session=session, user_id=current_user.id, skip=skip, limit=limit
    )
    return OrdersPublic(
        data=[OrderPublic.model_validate(order) for order in orders],
        count=count,
    )


@router.get("/orders/{order_id}", response_model=OrderPublic)
def read_order(
    session: SessionDep, current_user: CurrentUser, order_id: uuid.UUID
) -> Any:
    """
    Get order details by ID.

    Users can only access their own orders unless they are superusers.
    """
    order = get_order_by_id(session=session, order_id=order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found",
        )
    if not current_user.is_superuser and order.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    return OrderPublic.model_validate(order)

