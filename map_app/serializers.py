from rest_framework import serializers
from opticalfiber_app.models import Company, Staff
from office.models import Office, Branch
from customer_app.models import Customer
from route_app.models import FiberRoute
from junction_app.models import JunctionBox, JunctionBoxDevice
from networkdevice_app.models import NetworkDevice, DevicePort


class DevicePortSerializer(serializers.ModelSerializer):
    class Meta:
        model = DevicePort
        fields = ['id', 'device', 'port_number', 'port_type', 'speed']
        read_only_fields = ['id', 'created_at', 'updated_at']

class NetworkDeviceSerializer(serializers.ModelSerializer):
    ports = DevicePortSerializer(many=True, read_only=True)
    class Meta:
        model = NetworkDevice
        fields = ['id', 'device_type', 'model_name', 'description', 'ratio', 'max_speed', 'color_coding', 'insertion_loss', 'return_loss', 'port_count', 'supported_protocols','ports']
        read_only_fields = ['id', 'created_at', 'updated_at']


class JunctionBoxDeviceSerializer(serializers.ModelSerializer):
    device = NetworkDeviceSerializer(read_only=True)
    class Meta:
        model = JunctionBoxDevice
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']

class JunctionBoxSerializer(serializers.ModelSerializer):
    devices = JunctionBoxDeviceSerializer(many=True, read_only=True)
    class Meta:
        model = JunctionBox
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']

class FiberRouteSerializer(serializers.ModelSerializer):
    office = serializers.PrimaryKeyRelatedField(queryset=Office.objects.all())
    created_by = serializers.PrimaryKeyRelatedField(queryset=Staff.objects.all())
    class Meta:
        model = FiberRoute
        fields = ['id', 'office', 'created_by', 'name', 'path', 'length_km', 'created_at', 'is_deleted']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
class OfficeSerializer(serializers.ModelSerializer):
    fiber_routes = FiberRouteSerializer(many=True, read_only=True)
    junction_boxes = JunctionBoxSerializer(many=True, read_only=True)
    class Meta:
        model = Office
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


class CompanySerializer(serializers.ModelSerializer):
    offices = OfficeSerializer(many=True, read_only=True)
    class Meta:
        model = Company
        fields = ['id', 'name', 'registration_number', 'logo', 'email', 'phone', 'address', 'website', 'created_at', 'updated_at', 'is_active', 'offices']
        read_only_fields = ['id', 'created_at', 'updated_at']
