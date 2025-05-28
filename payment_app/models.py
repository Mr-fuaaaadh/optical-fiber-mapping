from django.db import models
from django.utils import timezone
from office.models import Company

class Payment(models.Model):
    company = models.ForeignKey(Company,on_delete=models.CASCADE,related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    duration_days = models.PositiveIntegerField(default=365)
    payment_date = models.DateTimeField(default=timezone.now)
    valid_until = models.DateTimeField(blank=True, null=True)
    transaction_id = models.CharField(max_length=100, unique=True)
    status = models.CharField(max_length=20,
        choices=[('pending', 'Pending'), ('success', 'Success'), ('failed', 'Failed')],
        default='pending'
    )
    payment_method = models.CharField(max_length=50, default='upi')
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    razorpay_order_id = models.CharField(max_length=100, blank=True, null=True, unique=True)

    def save(self, *args, **kwargs):
        if not self.valid_until and self.status == 'success':
            self.valid_until = self.payment_date + timezone.timedelta(days=self.duration_days)
        super().save(*args, **kwargs)
