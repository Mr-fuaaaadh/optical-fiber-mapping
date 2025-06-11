from rest_framework import serializers
from .models import Company, Staff

class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = '__all__'

class StaffSerializer(serializers.ModelSerializer):
    class Meta :
        model = Staff
        fields = "__all__"

class CompanyStaffSerializers(serializers.ModelSerializer):
    staffs = StaffSerializer(many=True, read_only=True) 
    class Meta:
        model = Company
        fields = "__all__"


class StaffLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()


class StaffProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Staff
        fields = ['id','name', 'email','profile_picture']