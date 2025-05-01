from django.urls import path
from .views import *

urlpatterns = [
    path('add/', OfficeView.as_view(), name='office-view'),
    path('management/<int:office_id>/', OfficeManagementView.as_view(), name='office-management-view-id'),
]