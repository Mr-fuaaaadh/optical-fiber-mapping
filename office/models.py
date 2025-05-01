from django.db import models
from opticalfiber_app.models import Company
# Create your models here.

class Office(models.Model):
    OFFICE_TYPES = (
        ('head', 'Head Office'),
        ('branch', 'Branch'),
        ('service', 'Service Center'),
    )

    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='offices')
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=50, choices=OFFICE_TYPES, default='branch')
    latitude = models.FloatField()
    longitude = models.FloatField()
    address = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    note = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = 'Office'
        verbose_name_plural = 'Offices'
