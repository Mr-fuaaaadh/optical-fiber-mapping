from serializers import ModelSerializer
from rest_framework import serializers
from .models import *



class NetworkDeviceSerializer(ModelSerializer):
    """
    Serializer for NetworkDevice model.
    """
    class Meta:
        model = NetworkDevice
        fields = "__all__"
        read_only_fields = ['c', 'updated_at']


class DevicePortSerializer(ModelSerializer):
    """
    Serializer for DevicePort model.
    """
    class Meta:
        model = DevicePort
        fields = "__all__"
        read_only_fields = ['created_at', 'updated_at']