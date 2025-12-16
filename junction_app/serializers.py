from rest_framework import serializers
from .models import *


class JunctionBoxSerializer(serializers.ModelSerializer):
    class Meta:
        model = JunctionBox
        fields = "__all__"
        read_only_fields = ['created_at']



class JunctionDeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = JunctionBoxDevice
        fields = "__all__"
        read_only_fields = ['created_at']