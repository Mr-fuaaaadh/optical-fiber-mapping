import httpx
import hmac
import hashlib
import base64
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

async def create_cashfree_order(order_id: str, amount, customer_email: str, customer_phone: str, return_url: str):
    base_url = "https://sandbox.cashfree.com/pg" if settings.CASHFREE_ENV.lower() == 'test' else "https://api.cashfree.com/pg"
    url = f"{base_url}/orders"
    payload = {
        "order_id": order_id,
        "order_amount": float(amount),
        "order_currency": "INR",
        "customer_details": {
            "customer_id": f"user_{order_id}",
            "customer_email": customer_email,
            "customer_phone": customer_phone,
        },
        "order_meta": {
            "return_url": return_url,
        },
    }
    headers = {
        "Content-Type": "application/json",
        "x-api-version": "2022-09-01",
        "x-client-id": settings.CASHFREE_APP_ID,
        "x-client-secret": settings.CASHFREE_SECRET_KEY,
    }
    async with httpx.AsyncClient(timeout=15) as client:
        try:
            response = await client.post(url, json=payload, headers=headers)
            logger.info(f"Cashfree order response: {response.status_code} - {response.text}")
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except httpx.HTTPError as e:
            logger.error(f"Failed to create Cashfree order: {str(e)}")
            return {"success": False, "error": "Request failed", "details": str(e)}

async def verify_cashfree_order(order_id: str):
    base_url = "https://sandbox.cashfree.com/pg" if settings.CASHFREE_ENV.lower() == 'test' else "https://api.cashfree.com/pg"
    url = f"{base_url}/orders/{order_id}"
    headers = {
        "x-api-version": "2022-09-01",
        "x-client-id": settings.CASHFREE_APP_ID,
        "x-client-secret": settings.CASHFREE_SECRET_KEY,
    }
    async with httpx.AsyncClient(timeout=15) as client:
        try:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Failed to verify Cashfree order {order_id}: {str(e)}")
            return {"error": "Verification failed", "details": str(e)}

def verify_webhook_signature(payload: str, signature: str) -> bool:
    secret = settings.CASHFREE_WEBHOOK_SECRET.encode()
    computed = base64.b64encode(hmac.new(secret, payload.encode(), hashlib.sha256).digest()).decode()
    return hmac.compare_digest(computed, signature)
