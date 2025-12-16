from django.urls import path
from .views import *


urlpatterns = [
    path('networkdevice/', NetworkDeviceListCreateAPIView.as_view(), name='networkdevice-list-create'),
    path('networkdevice/<int:pk>/', NetworkDeviceRetrieveUpdateDestroyAPIView.as_view(), name='networkdevice-detail'),
    path('networkdevice/<int:pk>/update/', NetworkDeviceRetrieveUpdateDestroyAPIView.as_view(), name='networkdevice-update'),
    path('networkdevice/<int:pk>/delete/', NetworkDeviceRetrieveUpdateDestroyAPIView.as_view(), name='networkdevice-delete'),


    path('deviceport/<int:device_id>/', DevicePortListCreateAPIView.as_view(), name='deviceport-list-create'),
    path('deviceport/<int:pk>/get/', DevicePortRetrieveUpdateDestroyAPIView.as_view(), name='deviceport-detail'),
    path('deviceport/<int:pk>/update/', DevicePortRetrieveUpdateDestroyAPIView.as_view(), name='deviceport-update'),
    path('deviceport/<int:pk>/delete/', DevicePortRetrieveUpdateDestroyAPIView.as_view(), name='deviceport-delete'),

]