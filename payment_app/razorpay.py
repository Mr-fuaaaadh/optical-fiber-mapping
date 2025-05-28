import httpx
from httpx import HTTPStatusError
from django.conf import settings
import hmac
import hashlib
import logging

logger = logging.getLogger(__name__)

class AsyncRazorpayClient:
    BASE_URL = "https://api.razorpay.com/v1/"

    def __init__(self):
        self.auth = (settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)

    async def create_order(self, amount_paise: int, currency: str = "INR", payment_capture: int = 1) -> dict:
        """
        Create Razorpay order asynchronously.
        """
        url = self.BASE_URL + "orders"
        payload = {
            "amount": amount_paise,
            "currency": currency,
            "payment_capture": payment_capture,
        }
        async with httpx.AsyncClient(auth=self.auth) as client:
            try:
                response = await client.post(url, json=payload)
                response.raise_for_status()
                return response.json()
            except HTTPStatusError as e:
                logger.error(f"Razorpay order creation failed: {str(e)}")
                raise RuntimeError(f"Razorpay order creation failed: {str(e)}")

    async def verify_signature(self, razorpay_order_id: str, razorpay_payment_id: str, razorpay_signature: str) -> bool:
        """
        Verify payment signature from Razorpay webhook or frontend callback.
        """
        msg = f"{razorpay_order_id}|{razorpay_payment_id}".encode()
        secret = settings.RAZORPAY_KEY_SECRET.encode()
        generated_signature = hmac.new(secret, msg, hashlib.sha256).hexdigest()
        return generated_signature == razorpay_signature
