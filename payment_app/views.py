from rest_framework.views import APIView
from opticalfiber_app.views import BaseAPIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from django.conf import settings
from .models import Payment
from .serializers import PaymentCreateSerializer, PaymentSerializer
from .cashfree_async import create_cashfree_order, verify_cashfree_order, verify_webhook_signature
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny
import uuid
import logging
import json
import asyncio
from opticalfiber_app.models import Staff
import requests

logger = logging.getLogger(__name__)

class InitiatePaymentAPI(BaseAPIView):
    async def post(self, request):
        auth_user, error = self.get_authenticated_user(request)
        if error:
            return Response({"error": error}, status=status.HTTP_400_BAD_REQUEST)

        company = auth_user.company
        amount = request.data.get('amount')
        email = auth_user.email
        phone = request.data.get('phone')

        if not phone:
            return Response({"error": "Phone number required"}, status=400)
        if not amount:
            return Response({"error": "Amount is required"}, status=400)

        transaction_id = str(uuid.uuid4())
        return_url = f"https://backend.fiberonix.in/api/payment/callback/?transaction_id={transaction_id}"

        payment = Payment.objects.create(
            company=company,
            amount=amount,
            transaction_id=transaction_id,
            status='pending',
            payment_method='cashfree'
        )

        response = await create_cashfree_order(transaction_id, amount, email, phone, return_url)
        if response.get('success'):
            data = response['data']
            payment.order_id = data.get('order_id')
            payment.payment_session_id = data.get('payment_session_id')
            payment.save()
            return Response({
                "payment_link": data["payments"]["url"],
                "order_id": data.get('order_id'),
                "payment_session_id": data.get('payment_session_id'),
                "transaction_id": transaction_id
            }, status=200)
        else:
            payment.status = 'failed'
            payment.save()
            return Response({
                "error": "Failed to create order",
                "details": response.get('details')
            }, status=500)

    def get_authenticated_user(self, request):
        try:
            auth_user = self.authentication(request)
            user_id = auth_user.get('id')
            if not user_id:
                return None, "Unauthorized access"
            staff_member = Staff.objects.select_related('company').get(pk=user_id)
            return staff_member, None
        except Staff.DoesNotExist:
            return None, "Staff member not found in the database."
        except Exception as e:
            return None, f"An error occurred while fetching staff details: {str(e)}"

class PaymentCallbackAPI(APIView):
    def get(self, request):
        transaction_id = request.GET.get('transaction_id')
        if not transaction_id:
            return Response({"error": "Missing transaction_id"}, status=400)
        payment = Payment.objects.filter(transaction_id=transaction_id).first()
        if not payment:
            return Response({"error": "Invalid transaction ID"}, status=404)
        url = f"https://sandbox.cashfree.com/pg/orders/{transaction_id}" if settings.CASHFREE_ENV == 'test' else f"https://api.cashfree.com/pg/orders/{transaction_id}"
        headers = {
            "x-api-version": "2022-09-01",
            "x-client-id": settings.CASHFREE_APP_ID,
            "x-client-secret": settings.CASHFREE_SECRET_KEY,
        }
        try:
            resp = requests.get(url, headers=headers, timeout=10)
            data = resp.json()
        except Exception as e:
            return Response({"error": "Error verifying payment", "details": str(e)}, status=500)
        order_status = data.get('order_status', '').upper()
        if order_status == 'PAID':
            if payment.status != 'success':
                payment.status = 'success'
                payment.valid_until = payment.payment_date + timezone.timedelta(days=payment.duration_days)
                payment.save()
            return Response({"message": "Payment successful and verified"}, status=200)
        elif order_status in ['FAILED', 'EXPIRED']:
            payment.status = 'failed'
            payment.save()
            return Response({"error": f"Payment failed: {order_status}"}, status=400)
        return Response({"message": f"Payment is still {order_status}"}, status=202)

from rest_framework.decorators import api_view
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
@api_view(['POST'])
@authentication_classes([])   # 🔥 REQUIRED
@permission_classes([AllowAny])  # 🔥 REQUIRED
def cashfree_webhook(request):
    try:
        data = request.data or {}
        logger.info(f"Cashfree Webhook Received: {data}")

        if data.get('type') == 'TEST_WEBHOOK':
            return Response(
                {"message": "Test webhook received"},
                status=status.HTTP_200_OK
            )

        # ✅ Signature verification
        payload = request.body.decode("utf-8")
        signature = request.headers.get("x-webhook-signature")

        if not signature:
            logger.warning("Webhook signature missing")
            return Response({"message": "Signature missing"}, status=200)

        if not verify_webhook_signature(payload, signature):
            logger.warning("Invalid webhook signature")
            return Response({"message": "Invalid signature"}, status=200)

        order = data.get("data", {}).get("order", {})
        order_id = order.get("order_id")
        status_received = order.get("order_status")

        if not order_id or not status_received:
            return Response({"message": "Invalid payload"}, status=200)

        payment = Payment.objects.filter(transaction_id=order_id).first()

        if not payment:
            logger.warning(f"Payment not found: {order_id}")
            return Response({"message": "Payment not found"}, status=200)

        # ✅ Idempotent handling
        if status_received == "PAID" and payment.status != "success":
            payment.status = "success"
            payment.valid_until = (
                payment.payment_date +
                timezone.timedelta(days=payment.duration_days)
            )
            payment.save(update_fields=["status", "valid_until"])

        elif status_received in ["FAILED", "CANCELLED", "EXPIRED"]:
            if payment.status != "failed":
                payment.status = "failed"
                payment.save(update_fields=["status"])

        return Response(
            {"message": "Webhook processed"},
            status=status.HTTP_200_OK
        )

    except Exception as e:
        logger.exception("Cashfree webhook error")
        return Response(
            {"message": "Webhook error"},
            status=status.HTTP_200_OK
        )
class VerifyPaymentAPI(APIView):
    def get(self, request, transaction_id):
        payment = Payment.objects.filter(transaction_id=transaction_id).first()
        if not payment:
            return Response({"error": "Invalid transaction ID"}, status=404)
        response = asyncio.run(verify_cashfree_order(transaction_id))
        if response.get('order_status') == 'PAID' and payment.status != 'success':
            payment.status = 'success'
            payment.valid_until = payment.payment_date + timezone.timedelta(days=payment.duration_days)
            payment.save()
        return Response({
            "status": payment.status,
            "valid_until": payment.valid_until,
        })

class CheckValidityAPI(APIView):
    def get(self, request, transaction_id):
        payment = Payment.objects.filter(transaction_id=transaction_id).first()
        if not payment:
            return Response({"error": "Invalid transaction ID"}, status=404)
        return Response({
            "is_valid": payment.is_valid,
            "valid_until": payment.valid_until,
        })
