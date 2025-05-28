from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from asgiref.sync import sync_to_async
from .serializers import PaymentCreateSerializer
from .models import Payment
from .razorpay import AsyncRazorpayClient
import uuid
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)


class CreatePaymentOrderAPIView(APIView):
    async def post(self, request):
        serializer = PaymentCreateSerializer(data=request.data)
        if not serializer.is_valid():
            logger.warning(f"Payment create validation failed: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        company = serializer.validated_data['company']
        amount = serializer.validated_data['amount']

        # Create initial payment record with pending status
        payment = Payment(
            company=company,
            amount=amount,
            status='pending',
            transaction_id=str(uuid.uuid4())
        )

        try:
            await sync_to_async(payment.save)()
        except Exception as e:
            logger.error(f"Failed to save Payment record: {e}", exc_info=True)
            return Response({"detail": "Internal server error saving payment."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        razorpay_client = AsyncRazorpayClient()
        try:
            order = await razorpay_client.create_order(int(amount * 100))
        except Exception as e:
            logger.error(f"Razorpay order creation failed: {e}", exc_info=True)
            # Consider also deleting the Payment record or marking as failed
            return Response({"detail": "Failed to create Razorpay order."}, status=status.HTTP_502_BAD_GATEWAY)

        payment.razorpay_order_id = order.get('id')
        try:
            await sync_to_async(payment.save)()
        except Exception as e:
            logger.error(f"Failed to update Payment with Razorpay order_id: {e}", exc_info=True)
            return Response({"detail": "Internal server error updating payment."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({
            "order_id": order.get('id'),
            "amount": order.get('amount'),
            "currency": order.get('currency'),
            "transaction_id": payment.transaction_id
        }, status=status.HTTP_201_CREATED)


class VerifyPaymentAPIView(APIView):
    async def post(self, request):
        data = request.data
        razorpay_order_id = data.get('razorpay_order_id')
        razorpay_payment_id = data.get('razorpay_payment_id')
        razorpay_signature = data.get('razorpay_signature')

        if not razorpay_order_id or not razorpay_payment_id or not razorpay_signature:
            logger.warning("Missing Razorpay payment verification fields")
            return Response({"detail": "Missing required fields."}, status=status.HTTP_400_BAD_REQUEST)

        razorpay_client = AsyncRazorpayClient()
        try:
            is_valid = await razorpay_client.verify_signature(
                razorpay_order_id, razorpay_payment_id, razorpay_signature
            )
        except Exception as e:
            logger.error(f"Error during Razorpay signature verification: {e}", exc_info=True)
            return Response({"detail": "Error verifying payment signature."}, status=status.HTTP_502_BAD_GATEWAY)

        if not is_valid:
            logger.warning(f"Invalid Razorpay signature for order {razorpay_order_id}")
            return Response({"detail": "Signature verification failed."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            payment = await sync_to_async(Payment.objects.get)(razorpay_order_id=razorpay_order_id)
        except Payment.DoesNotExist:
            logger.warning(f"Payment with razorpay_order_id {razorpay_order_id} not found.")
            return Response({"detail": "Payment record not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error fetching payment record: {e}", exc_info=True)
            return Response({"detail": "Internal server error fetching payment."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        if payment.status == 'success':
            logger.info(f"Payment already verified for order {razorpay_order_id}")
            return Response({"detail": "Payment already verified."}, status=status.HTTP_200_OK)

        payment.status = 'success'
        payment.payment_date = timezone.now()

        try:
            await sync_to_async(payment.save)()
        except Exception as e:
            logger.error(f"Error saving payment update: {e}", exc_info=True)
            return Response({"detail": "Internal server error updating payment."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({"detail": "Payment verified successfully."}, status=status.HTTP_200_OK)
