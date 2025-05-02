from rest_framework import serializers
from .models import FiberRoute

class FiberRouteSerializer(serializers.ModelSerializer):
    class Meta :
        model = FiberRoute
        fields = "__all__"
        read_only_fields = ['created_at']








