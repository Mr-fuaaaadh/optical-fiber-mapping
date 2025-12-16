from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Admin Panel
    path('admin/', admin.site.urls),

    # API Endpoints
    path('api/opticalfiber/', include('opticalfiber_app.urls')),  # User registration, login, etc.
    path('api/office/', include('office.urls')),                  # Office-related endpoints
    path('api/route/', include('route_app.urls')),                # Route management
    path('api/junction/', include('junction_app.urls')),          # Junction details
    path('api/network-device/', include('networkdevice_app.urls')),  # Network device data
    path('api/customer/', include('customer_app.urls')),          # Customer info
    path('api/map/', include('map_app.urls')),                    # Map-related endpoints
    path('api/payment/',include('payment_app.urls'))
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
