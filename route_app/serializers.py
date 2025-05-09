from rest_framework import serializers
from .models import FiberRoute
from django.core.exceptions import ValidationError

class FiberRouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = FiberRoute
        fields = '__all__'


