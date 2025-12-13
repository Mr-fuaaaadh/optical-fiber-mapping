from rest_framework import serializers
from .models import Payment

class PaymentCreateSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    currency = serializers.ChoiceField(choices=[('INR', 'INR')], default='INR')
    phone = serializers.CharField(max_length=15)
    email = serializers.EmailField()

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than zero.")
        return value

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['id', 'company', 'amount', 'transaction_id', 'status', 'valid_until',
                  'payment_method', 'order_id', 'payment_session_id', 'products',
                  'created_at', 'payment_date', 'duration_days', 'is_valid']
        read_only_fields = ['transaction_id', 'status', 'valid_until', 'order_id', 'payment_session_id']
