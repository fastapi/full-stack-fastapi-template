"""Razorpay payment gateway service integration."""

from typing import Any

import razorpay
from razorpay.errors import BadRequestError, ServerError

from app.core.config import settings


class RazorpayClient:
    """Wrapper for Razorpay client with payment operations."""

    def __init__(self) -> None:
        """Initialize Razorpay client with API keys from settings."""
        if not settings.razorpay_enabled:
            raise ValueError(
                "Razorpay keys are not configured. "
                "Please set RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET in environment variables."
            )
        self.client = razorpay.Client(
            auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
        )

    def create_order(
        self, amount: int, currency: str, receipt: str | None = None, notes: dict[str, str] | None = None
    ) -> dict[str, Any]:
        """
        Create a Razorpay order.

        Args:
            amount: Amount in smallest currency unit (paise for INR)
            currency: Currency code (default: INR)
            receipt: Receipt identifier (optional)
            notes: Additional notes as key-value pairs (optional)

        Returns:
            Dictionary containing Razorpay order details including order_id

        Raises:
            BadRequestError: If the request is invalid
            ServerError: If Razorpay server returns an error
        """
        try:
            order_data: dict[str, Any] = {
                "amount": amount,
                "currency": currency,
            }
            if receipt:
                order_data["receipt"] = receipt
            if notes:
                order_data["notes"] = notes

            order = self.client.order.create(data=order_data)
            return order
        except (BadRequestError, ServerError) as e:
            raise ValueError(f"Failed to create Razorpay order: {str(e)}") from e

    def verify_payment_signature(
        self, order_id: str, payment_id: str, signature: str
    ) -> bool:
        """
        Verify payment signature to ensure authenticity.

        Args:
            order_id: Razorpay order ID
            payment_id: Razorpay payment ID
            signature: Payment signature from Razorpay

        Returns:
            True if signature is valid, False otherwise
        """
        try:
            params = {
                "razorpay_order_id": order_id,
                "razorpay_payment_id": payment_id,
                "razorpay_signature": signature,
            }
            self.client.utility.verify_payment_signature(params)
            return True
        except razorpay.errors.SignatureVerificationError:
            return False
        except Exception as e:
            raise ValueError(f"Error verifying payment signature: {str(e)}") from e

    def get_order(self, razorpay_order_id: str) -> dict[str, Any]:
        """
        Fetch order details from Razorpay.

        Args:
            razorpay_order_id: Razorpay order ID

        Returns:
            Dictionary containing order details

        Raises:
            BadRequestError: If order not found
            ServerError: If Razorpay server returns an error
        """
        try:
            order = self.client.order.fetch(razorpay_order_id)
            return order
        except (BadRequestError, ServerError) as e:
            raise ValueError(f"Failed to fetch Razorpay order: {str(e)}") from e

    def capture_payment(self, payment_id: str, amount: int) -> dict[str, Any]:
        """
        Capture a payment (for manual capture flow).

        Args:
            payment_id: Razorpay payment ID
            amount: Amount to capture in smallest currency unit

        Returns:
            Dictionary containing capture details

        Raises:
            BadRequestError: If capture fails
            ServerError: If Razorpay server returns an error
        """
        try:
            capture_data = {"amount": amount}
            payment = self.client.payment.capture(payment_id, capture_data)
            return payment
        except (BadRequestError, ServerError) as e:
            raise ValueError(f"Failed to capture payment: {str(e)}") from e

    def verify_webhook_signature(self, payload: str, signature: str) -> bool:
        """
        Verify webhook signature.

        Args:
            payload: Webhook payload as string
            signature: Webhook signature from Razorpay

        Returns:
            True if signature is valid, False otherwise
        """
        if not settings.RAZORPAY_WEBHOOK_SECRET:
            return False
        try:
            self.client.utility.verify_webhook_signature(
                payload, signature, settings.RAZORPAY_WEBHOOK_SECRET
            )
            return True
        except razorpay.errors.SignatureVerificationError:
            return False
        except Exception as e:
            raise ValueError(f"Error verifying webhook signature: {str(e)}") from e


def get_razorpay_client() -> RazorpayClient:
    """
    Get Razorpay client instance.

    Returns:
        RazorpayClient instance

    Raises:
        ValueError: If Razorpay is not configured
    """
    return RazorpayClient()

