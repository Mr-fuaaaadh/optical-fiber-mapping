# views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import hashlib
from .models import Payment
from office.models import Company

API_KEY = "0569a75e-6340-41c4-bdaa-32756bd1e293"
SALT = "f57e3797163532e72d0d9ba9d289cb30cff4ee45"
GATEWAY_URL = "https://uat.ablepay.in/v2/paymentrequest"

REQUIRED_FIELDS = [
    "company", "amount", "transaction_id", "notes", "razorpay_order_id", "udf1", "udf2", "udf3", "udf4", "udf5"
]

class PaymentRequestAPIView(APIView):
    def post(self, request):
        posted = request.data

        # Check for required fields
        missing_fields = [field for field in REQUIRED_FIELDS if not posted.get(field)]
        if missing_fields:
            return Response({
                "success": False,
                "message": f"Missing required fields: {', '.join(missing_fields)}"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate company exists
        company_id = posted.get("company")
        try:
            company = Company.objects.get(id=company_id)
        except Company.DoesNotExist:
            return Response({
                "success": False,
                "message": "Invalid company ID."
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Generate hash string safely
        hash_string = SALT
        for key in REQUIRED_FIELDS:
            value = str(posted.get(key, '')).strip()
            hash_string += f"|{value}"

        hash_val = hashlib.sha512(hash_string.encode()).hexdigest().upper()

        return Response({
            "success": True,
            "api_key": API_KEY,
            "hash": hash_val,
            "gateway_url": GATEWAY_URL,
            "form_data": posted
        }, status=status.HTTP_200_OK)


@method_decorator(csrf_exempt, name='dispatch')
class PaymentResponseAPIView(APIView):
    def post(self, request):
        data = request.POST or request.data
        hash_received = data.get("hash")

        hash_string = SALT
        for k in sorted(data):
            if k != "hash" and len(str(data[k])) > 0:
                hash_string += "|" + str(data[k])

        calculated_hash = hashlib.sha512(hash_string.encode()).hexdigest().upper()

        if hash_received != calculated_hash:
            return Response({
                "success": False,
                "message": "Hash mismatch. Transaction Failed."
            }, status=status.HTTP_400_BAD_REQUEST)

        status_code = data.get("response_code")
        transaction_id = data.get("transaction_id")
        amount = data.get("amount")
        company_id = data.get("udf1")  
        
        try:
            company = Company.objects.get(id=company_id)
            payment = Payment.objects.create(
                company=company,
                amount=amount,
                transaction_id=transaction_id,
                status="success" if status_code == "0" else "failed",
                payment_method="upi",
                payment_date=timezone.now(),
                notes=data.get("response_message")
            )
        except Company.DoesNotExist:
            return Response({
                "success": False,
                "message": "Company not found."
            }, status=status.HTTP_404_NOT_FOUND)

        if status_code == "0":
            return Response({
                "success": True,
                "message": "Transaction successful",
                "transaction_id": transaction_id,
                "amount": amount
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                "success": False,
                "message": "Transaction failed",
                "transaction_id": transaction_id
            }, status=status.HTTP_400_BAD_REQUEST)
