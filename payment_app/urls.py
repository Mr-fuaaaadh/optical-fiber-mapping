from django.urls import path
from .views import CreatePaymentOrderAPIView, VerifyPaymentAPIView

urlpatterns = [
    path('create-payment-order/', CreatePaymentOrderAPIView.as_view(), name='create_payment_order'),
    path('verify-payment/', VerifyPaymentAPIView.as_view(), name='verify_payment'),
]
