from rest_framework.views import APIView
from opticalfiber_app.views import BaseAPIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from django.conf import settings
from .models import Payment
from .serializers import *
from .cashfree import create_cashfree_order
import uuid
from opticalfiber_app.models import Staff
import requests
import logging
import json

logger = logging.getLogger(__name__)


class InitiatePaymentAPI(BaseAPIView):
    def post(self, request):
        auth_user, error = self.get_authenticated_user(request)
        if error:
            return Response({"error": error}, status=status.HTTP_400_BAD_REQUEST)
        
        user = auth_user.pk
        company = auth_user.company
        amount = request.data.get('amount')
        email = auth_user.email
        phone = request.data.get('phone')

        if not phone:
            return Response({"error": "Phone number required"}, status=400)
        if not amount:
            return Response({"error": "Amount is required"}, status=400)

        transaction_id = str(uuid.uuid4())
        return_url = f"https://yourdomain.com/api/payment/callback/?transaction_id={transaction_id}"

        payment = Payment.objects.create(
            company=company,
            amount=amount,
            transaction_id=transaction_id,
            status='pending',
            payment_method='cashfree'
        )

        response = create_cashfree_order(transaction_id, amount, email, phone, return_url)

        if response.get("success"):
            data = response["data"]
            return Response({
                "payment_link": data["payments"]["url"],
                "order_id": data["order_id"],
                "payment_session_id": data.get("payment_session_id"),
                "transaction_id": transaction_id
            }, status=200)
        else:
            payment.status = 'failed'
            payment.save()
            return Response({
                "error": "Failed to create order",
                "details": response.get("details")
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
        transaction_id = request.data.get('transaction_id')

        if not transaction_id:
            return Response({"error": "Missing transaction_id"}, status=status.HTTP_400_BAD_REQUEST)

        payment = Payment.objects.filter(transaction_id=transaction_id).first()
        if not payment:
            return Response({"error": "Invalid transaction ID"}, status=status.HTTP_404_NOT_FOUND)

        # ✅ VERIFY with Cashfree API
        url = f"https://sandbox.cashfree.com/pg/orders/{transaction_id}" if settings.CASHFREE_ENV == 'test' else f"https://api.cashfree.com/pg/orders/{transaction_id}"

        headers = {
            "x-api-version": "2022-09-01",
            "x-client-id": settings.CASHFREE_APP_ID,
            "x-client-secret": settings.CASHFREE_SECRET_KEY,
        }

        try:
            response = requests.get(url, headers=headers, timeout=10)
            data = response.json()
        except Exception as e:
            return Response({"error": "Error verifying payment", "details": str(e)}, status=500)

        order_status = data.get("order_status", "").upper()

        if order_status == "PAID":
            if payment.status != 'success':
                payment.status = 'success'
                payment.valid_until = payment.payment_date + timezone.timedelta(days=payment.duration_days)
                payment.save()
            return Response({"message": "Payment successful and verified"}, status=200)

        elif order_status in ["FAILED", "EXPIRED"]:
            payment.status = 'failed'
            payment.save()
            return Response({"error": f"Payment failed: {order_status}"}, status=400)

        else:
            return Response({"message": f"Payment is still {order_status}"}, status=202)




from rest_framework.decorators import api_view
from .cashfree import verify_webhook_signature

@api_view(['POST'])
def cashfree_webhook(request):
    try:
        payload = request.body.decode('utf-8')
        signature = request.headers.get('x-webhook-signature')
        if not signature:
            return Response({"error": "Signature missing"}, status=400)

        # Signature validation
        if not verify_webhook_signature(payload, signature):
            logger.warning("Invalid Cashfree webhook signature")
            return Response({"error": "Invalid signature"}, status=403)

        data = json.loads(payload)
        order = data.get("order", {})
        order_id = order.get('order_id')
        status_received = order.get('order_status')

        if not order_id or not status_received:
            return Response({"error": "Invalid payload"}, status=400)

        payment = Payment.objects.filter(transaction_id=order_id).first()
        if not payment:
            return Response({"error": "Transaction not found"}, status=404)

        if status_received == "PAID" and payment.status != "success":
            payment.status = "success"
            payment.valid_until = payment.payment_date + timezone.timedelta(days=payment.duration_days)
            payment.save()
            logger.info(f"Payment {order_id} marked as success")

        elif status_received in ["FAILED", "CANCELLED", "EXPIRED"]:
            payment.status = "failed"
            payment.save()
            logger.info(f"Payment {order_id} marked as failed")

        return Response({"message": "Webhook processed successfully"}, status=200)

    except Exception as e:
        logger.error(f"Error processing Cashfree webhook: {str(e)}")
        return Response({"error": "Internal server error"}, status=500)


class VerifyPaymentAPI(APIView):
    def get(self, request, transaction_id):
        from cashfree import verify_cashfree_order

        payment = Payment.objects.filter(transaction_id=transaction_id).first()
        if not payment:
            return Response({"error": "Invalid transaction ID"}, status=404)

        response = verify_cashfree_order(transaction_id)
        if response.get("order_status") == "PAID" and payment.status != "success":
            payment.status = "success"
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
            "valid_until": payment.valid_until
        })
