from django.urls import path
from .views import (
    InitiatePaymentAPI,
    PaymentCallbackAPI,
    cashfree_webhook,
    PaymentListAPI
)

urlpatterns = [
    path("initiate/", InitiatePaymentAPI.as_view()),
    path("callback/", PaymentCallbackAPI.as_view()),
    path("webhook/", cashfree_webhook),
    path("list/", PaymentListAPI.as_view()),
]
