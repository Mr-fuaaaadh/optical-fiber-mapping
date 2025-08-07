from rest_framework import serializers

class PaymentCreateSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    currency = serializers.ChoiceField(choices=[('INR', 'INR')], default='INR')
    phone = serializers.CharField(max_length=15)
    email = serializers.EmailField()

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than zero.")
        return value

