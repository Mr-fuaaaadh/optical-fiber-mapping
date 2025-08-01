from django.urls import path
from .views import *


urlpatterns = [
    path('add/', FiberRouteCreateView.as_view(), name='route-add'),
    path('list/<int:pk>/', FiberRouteListView.as_view(), name='route-list'),
    path('management/<int:fiber_route_id>/', FiberRouteManagementView.as_view(), name='route-management'),
    path('management/<int:fiber_route_id>/delete/', FiberRouteManagementView.as_view(), name='route-management-delete'),
    path('management/<int:fiber_route_id>/update/', FiberRouteManagementView.as_view(), name='route-management-update'),
]