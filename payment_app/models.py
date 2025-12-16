from django.db import models
from django.utils import timezone
from office.models import Company

class Payment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('success', 'Success'),
        ('failed', 'Failed')
    ]

    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    duration_days = models.PositiveIntegerField(default=365)
    payment_date = models.DateTimeField(default=timezone.now)
    valid_until = models.DateTimeField(blank=True, null=True)

    transaction_id = models.CharField(max_length=100, unique=True) 
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_method = models.CharField(max_length=50, default='upi')
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    order_id = models.CharField(max_length=100, blank=True, null=True, unique=True)
    payment_session_id = models.CharField(max_length=500, blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.valid_until and self.status == 'success':
            self.valid_until = self.payment_date + timezone.timedelta(days=self.duration_days)
        super().save(*args, **kwargs)

    @property
    def is_valid(self):
        return self.status == "success" and (self.valid_until and timezone.now() <= self.valid_until)

    def mark_success(self):
        """Mark payment as success and calculate validity"""
        self.status = 'success'
        self.valid_until = self.payment_date + timezone.timedelta(days=self.duration_days)
        self.save()

    def mark_failed(self):
        """Mark payment as failed"""
        self.status = 'failed'
        self.save()

    def __str__(self):
        return f"{self.company.name} - {self.amount} ({self.status})"
