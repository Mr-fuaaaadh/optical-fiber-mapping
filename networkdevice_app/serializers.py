from .models import *
from rest_framework import serializers


class NetworkDeviceSerializer(serializers.ModelSerializer):
    """
    Serializer for NetworkDevice model.
    """
    class Meta:
        model = NetworkDevice
        fields = "__all__"
        read_only_fields = ['c', 'updated_at']


class DevicePortSerializer(serializers.ModelSerializer):
    """
    Serializer for DevicePort model.
    """
    class Meta:
        model = DevicePort
        fields = "__all__"
        read_only_fields = ['created_at', 'updated_at']