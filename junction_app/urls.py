from django.urls import path
from .views import JunctionAPIView, JunctionDeviceAPIView, JunctionDeviceDetailAPIView, JunctionDetailAPIView

urlpatterns = [
    path('add/', JunctionAPIView.as_view(), name='add_junction'),
    path('get/', JunctionAPIView.as_view(), name='remove_junction'),
    path('get/<int:pk>/', JunctionDetailAPIView.as_view(), name='get_junction'),
    path('get/<int:pk>/delete/', JunctionDetailAPIView.as_view(), name='delete_junction'),
    path('get/<int:pk>/update/', JunctionDetailAPIView.as_view(), name='update_junction'),


    path('get/<int:pk>/add_device/', JunctionDeviceAPIView.as_view(), name='add_device_to_junction'),
    path('get/<int:pk>/remove_device/', JunctionDeviceDetailAPIView.as_view(), name='remove_device_from_junction'),
    path('get/<int:pk>/update_device/', JunctionDeviceDetailAPIView.as_view(), name='update_device_in_junction'),
    path('get/<int:pk>/get_device/', JunctionDeviceDetailAPIView.as_view(), name='get_device_in_junction'),
    path('get/<int:pk>/get_all_devices/', JunctionDeviceAPIView.as_view(), name='get_all_devices_in_junction'),
]