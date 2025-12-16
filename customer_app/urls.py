from django.urls import path
from .views import *


urlpatterns = [

    path('add/', CustomerAPIView.as_view(), name='customer-view'),
    path('list/<int:office_id>/', CustomerListView.as_view(), name='customer-list-view'),
    path('management/<int:customer_id>/', CustomerManagementAPIView.as_view(), name='customer-management-view-id'),

]
