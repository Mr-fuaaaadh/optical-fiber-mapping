from rest_framework import serializers
from .models import Office



class OfficeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Office
        fields = '__all__'  # Include all fields from the Office model
        read_only_fields = ['company', 'created_at']

    def create(self, validated_data):
        """
        Create and return a new `Office` instance, given the validated data.
        """
        return Office.objects.create(**validated_data)  # Create a new Office instance with the validated data