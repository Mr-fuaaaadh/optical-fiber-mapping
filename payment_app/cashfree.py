
import requests
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

def create_cashfree_order(order_id, amount, customer_email, customer_phone, return_url):
    url = "https://sandbox.cashfree.com/pg/orders" if settings.CASHFREE_ENV.lower() == 'test' else "https://api.cashfree.com/pg/orders"
    
    headers = {
        "Content-Type": "application/json",
        "x-api-version": "2022-09-01",
        "x-client-id": settings.CASHFREE_APP_ID,
        "x-client-secret": settings.CASHFREE_SECRET_KEY
    }

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
            "return_url": return_url
        }
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        logger.info(f"Cashfree order response: {response.status_code} - {response.text}")

        if response.status_code == 200:
            return {
                "success": True,
                "data": response.json()
            }
        else:
            logger.error(f"Failed to create Cashfree order: {response.status_code} - {response.text}")
            return {
                "success": False,
                "error": "Failed to create order",
                "details": response.json()
            }

    except requests.exceptions.RequestException as e:
        logger.error(f"Exception occurred while creating Cashfree order: {str(e)}")
        return {
            "success": False,
            "error": "RequestException",
            "details": str(e)
        }

import hmac
import hashlib
import base64
from django.conf import settings

def verify_webhook_signature(payload: str, signature: str) -> bool:
    secret = settings.CASHFREE_WEBHOOK_SECRET.encode()
    computed = base64.b64encode(
        hmac.new(secret, payload.encode(), hashlib.sha256).digest()
    ).decode()

    return hmac.compare_digest(computed, signature)


def verify_cashfree_order(order_id):
    url = f"https://sandbox.cashfree.com/pg/orders/{order_id}" if settings.CASHFREE_ENV == 'TEST' else f"https://api.cashfree.com/pg/orders/{order_id}"

    headers = {
        "x-api-version": "2022-09-01",
        "x-client-id": settings.CASHFREE_APP_ID,
        "x-client-secret": settings.CASHFREE_SECRET_KEY
    }

    response = requests.get(url, headers=headers)
    return response.json()
