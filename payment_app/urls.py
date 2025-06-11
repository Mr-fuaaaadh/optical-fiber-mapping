from django.urls import path
from .views import PaymentRequestAPIView, PaymentResponseAPIView

urlpatterns = [
    path('create-payment-order/', PaymentRequestAPIView.as_view(), name='create_payment_order'),
    path('verify-payment/', PaymentResponseAPIView.as_view(), name='verify_payment'),
]
