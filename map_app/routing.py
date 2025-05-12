from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/map-data/$', consumers.MapDataConsumer.as_asgi()),
]
