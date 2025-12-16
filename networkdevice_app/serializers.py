from .models import *
from rest_framework import serializers
from .models import Design, CouplerCalculation


class NetworkDeviceSerializer(serializers.ModelSerializer):
    """
    Serializer for NetworkDevice model with all fields required and error handling.
    """

    class Meta:
        model = NetworkDevice
        fields = "__all__"
        read_only_fields = ['created_at', 'updated_at']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Mark all non-readonly fields as required
        for field_name, field in self.fields.items():
            if field_name not in self.Meta.read_only_fields:
                field.required = True
                field.allow_null = False
                if isinstance(field, serializers.CharField):
                    field.allow_blank = False

    def validate(self, data):
        errors = {}

        # Example: validate coordinates range
        if 'latitude' in data and not (-90 <= data['latitude'] <= 90):
            errors['latitude'] = 'Latitude must be between -90 and 90.'

        if 'logitutde' in data and not (-180 <= data['logitutde'] <= 180):
            errors['logitutde'] = 'Longitude must be between -180 and 180.'

        # Example: enforce that `max_speed` is positive if provided
        if 'max_speed' in data and data['max_speed'] is not None:
            if data['max_speed'] <= 0:
                errors['max_speed'] = 'Maximum speed must be a positive number.'

        # Example: validate insertion and return loss
        if 'insertion_loss' in data and data['insertion_loss'] is not None:
            if data['insertion_loss'] < 0:
                errors['insertion_loss'] = 'Insertion loss cannot be negative.'

        if 'return_loss' in data and data['return_loss'] is not None:
            if data['return_loss'] < 0:
                errors['return_loss'] = 'Return loss cannot be negative.'

        # Raise validation errors if any were collected
        if errors:
            raise serializers.ValidationError(errors)

        return data


class DevicePortSerializer(serializers.ModelSerializer):
    """
    Serializer for DevicePort model.
    """
    class Meta:
        model = DevicePort
        fields = "__all__"
        read_only_fields = ['created_at', 'updated_at']



class DevicePortViewSerializers(serializers.ModelSerializer):
    ports = DevicePortSerializer(read_only = True, many =True)
    class Meta :
        model = NetworkDevice
        fields = "__all__"



from rest_framework import serializers
from .models import Design, CouplerCalculation

class CouplerCalculationSerializer(serializers.ModelSerializer):
    class Meta:
        model = CouplerCalculation
        fields = ["id", "coupler_ratio", "tap_km", "tap_output_dbm", "throughput_km", "through_output_dbm"]

class DesignSerializer(serializers.ModelSerializer):
    couplers = CouplerCalculationSerializer(many=True)  # nested serializer

    class Meta:
        model = Design
        fields = ["id", "name", "input_power", "couplers"]

    def create(self, validated_data):
        couplers_data = validated_data.pop("couplers", [])
        company = self.context["company"]  # get logged-in user's company
        design = Design.objects.create(company=company, **validated_data)

        # create all couplers at once
        for coupler_data in couplers_data:
            CouplerCalculation.objects.create(design=design, **coupler_data)

        return design
    





