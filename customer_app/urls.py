from django.urls import path
from .views import *


urlpatterns = [

    path('add/', CustomerAPIView.as_view(), name='customer-view'),
    path('management/<int:customer_id>/', CustomerManagementAPIView.as_view(), name='customer-management-view-id'),

]