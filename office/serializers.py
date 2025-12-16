from rest_framework import serializers
from .models import Office, Branch



class OfficeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Office
        fields = '__all__'  
        read_only_fields = ['company', 'created_at']

    def create(self, validated_data):
        """
        Create and return a new `Office` instance, given the validated data.
        """
        return Office.objects.create(**validated_data)  
    



class BranchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Branch
        fields = '__all__'  
        read_only_fields = ['created_at']

    def create(self, validated_data):
        """
        Create and return a new `Branch` instance, given the validated data.
        """
        return Branch.objects.create(**validated_data)