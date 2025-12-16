import requests
import hmac
import hashlib
import base64
from django.conf import settings

BASE_URL = "https://sandbox.cashfree.com/pg" if settings.CASHFREE_ENV == "test" else "https://api.cashfree.com/pg"

HEADERS = {
    "Content-Type": "application/json",
    "x-api-version": "2022-09-01",
    "x-client-id": settings.CASHFREE_APP_ID,
    "x-client-secret": settings.CASHFREE_SECRET_KEY,
}


def create_cashfree_order(order_id, amount, email, phone, return_url):
    url = f"{BASE_URL}/orders"
    payload = {
        "order_id": order_id,
        "order_amount": float(amount),
        "order_currency": "INR",
        "customer_details": {
            "customer_id": order_id,
            "customer_email": email,
            "customer_phone": phone,
        },
        "order_meta": {"return_url": return_url},
    }

    response = requests.post(url, json=payload, headers=HEADERS, timeout=15)
    response.raise_for_status()
    return response.json()


def verify_cashfree_order(order_id):
    url = f"{BASE_URL}/orders/{order_id}"
    response = requests.get(url, headers=HEADERS, timeout=10)
    response.raise_for_status()
    return response.json()


def verify_webhook_signature(payload, signature):
    secret = settings.CASHFREE_WEBHOOK_SECRET.encode()
    computed = base64.b64encode(
        hmac.new(secret, payload.encode(), hashlib.sha256).digest()
    ).decode()
    return hmac.compare_digest(computed, signature)
