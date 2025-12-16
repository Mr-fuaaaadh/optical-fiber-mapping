import uuid
import json
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from .models import Payment
from .cashfree_async import (
    create_cashfree_order,
    verify_cashfree_order,
    verify_webhook_signature,
)
from django.conf import settings
from opticalfiber_app.views import BaseAPIView
from opticalfiber_app.models import Staff


class InitiatePaymentAPI(BaseAPIView):
    def post(self, request):
        user, error = self.get_authenticated_user(request)
        if error:
            return Response({"error": error}, status=401)

        amount = request.data.get("amount")
        phone = request.data.get("phone")

        if not amount or not phone:
            return Response({"error": "Amount and phone required"}, status=400)

        transaction_id = str(uuid.uuid4())

        payment = Payment.objects.create(
            company=user.company,
            amount=amount,
            transaction_id=transaction_id,
            status="pending",
            payment_method="cashfree",
        )

        return_url = f"{settings.CASHFREE_RETURN_URL}?transaction_id={transaction_id}"

        try:
            data = create_cashfree_order(
                order_id=transaction_id,
                amount=amount,
                email=user.email,
                phone=phone,
                return_url=return_url,
            )

            payment.order_id = data["order_id"]
            payment.payment_session_id = data["payment_session_id"]
            payment.save()

            return Response(
                {
                    "payment_session_id": data["payment_session_id"],
                    "order_id": data["order_id"],
                    "transaction_id": transaction_id,
                },
                status=200
            )

        except Exception as e:
            payment.mark_failed()
            return Response({"error": str(e)}, status=500)

    def get_authenticated_user(self, request):
        auth = self.authentication(request)

        # ❌ If authentication() returned a Response (error)
        if isinstance(auth, Response):
            return None, "Unauthorized"

        user_id = auth.get("id")
        if not user_id:
            return None, "Invalid authentication payload"

        try:
            staff = Staff.objects.select_related("company").get(pk=user_id)
            return staff, None
        except Staff.DoesNotExist:
            return None, "Staff not found"





class PaymentCallbackAPI(APIView):
    def get(self, request):
        transaction_id = request.GET.get("transaction_id")
        payment = Payment.objects.filter(transaction_id=transaction_id).first()

        if not payment or not payment.order_id:
            return Response({"error": "Invalid transaction"}, status=404)

        data = verify_cashfree_order(payment.order_id)

        if data.get("order_status") == "PAID":
            payment.mark_success()
            return Response({"message": "Payment successful"})

        payment.mark_failed()
        return Response({"error": "Payment failed"}, status=400)
    


@csrf_exempt
@api_view(["POST"])
def cashfree_webhook(request):
    try:
        payload = request.body.decode("utf-8")

        if settings.CASHFREE_ENV == "test":
            data = json.loads(payload)
            return Response({"message": "Test webhook received"}, status=200)

        # ---- Production verification below ----
        signature = request.META.get("HTTP_X_WEBHOOK_SIGNATURE")
        timestamp = request.META.get("HTTP_X_WEBHOOK_TIMESTAMP")

        if not verify_webhook_signature(payload, signature, timestamp):
            return Response({"error": "Invalid signature"}, status=401)

        data = json.loads(payload)

        order = data.get("data", {}).get("order", {})
        order_id = order.get("order_id")
        order_status = order.get("order_status")

        payment = Payment.objects.filter(order_id=order_id).first()
        if not payment:
            return Response({"message": "Order not found but webhook accepted"}, status=200)

        if order_status == "PAID":
            payment.mark_success()
        elif order_status in ["FAILED", "CANCELLED", "EXPIRED"]:
            payment.mark_failed()

        return Response({"message": "Webhook processed"}, status=200)

    except Exception as e:
        return Response({"error": str(e)}, status=500)




