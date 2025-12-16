from rest_framework import serializers
from .models import FiberRoute
from django.core.exceptions import ValidationError
from django.db.models import Sum
from office.models import Office

class FiberRouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = FiberRoute
        fields = '__all__'


class FiberRouteWithTotalSerializer(serializers.ModelSerializer):
    total_km = serializers.SerializerMethodField()

    class Meta:
        model = FiberRoute
        fields = '__all__'  # or list all fields explicitly + 'total_km'

    def get_total_km(self, obj):
        company_id = obj.office.company_id
        total = FiberRoute.objects.filter(
            office__company_id=company_id,
            is_deleted=False
        ).aggregate(Sum('length_km'))['length_km__sum']
        return total or 0