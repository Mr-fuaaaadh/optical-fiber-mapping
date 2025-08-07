from django.urls import path
from .views import (
    InitiatePaymentAPI,
    PaymentCallbackAPI,
    cashfree_webhook,
    VerifyPaymentAPI,
    CheckValidityAPI
)

urlpatterns = [
    path('initiate/', InitiatePaymentAPI.as_view()),
    path('callback/', PaymentCallbackAPI.as_view()),
    path('webhook/', cashfree_webhook),
    path('verify/<str:transaction_id>/', VerifyPaymentAPI.as_view()),
    path('validity/<str:transaction_id>/', CheckValidityAPI.as_view()),
]
