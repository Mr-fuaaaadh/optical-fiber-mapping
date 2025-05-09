from office.models import Office
from django.db import models
from opticalfiber_app.models import Staff  
from django.utils.text import slugify
from decimal import Decimal

class FiberRoute(models.Model):
    office = models.ForeignKey(Office, on_delete=models.CASCADE, related_name='fiber_routes', db_index=True)
    created_by = models.ForeignKey(Staff, on_delete=models.CASCADE, null=True, blank=True, related_name='fiber_routes_created')
    name = models.CharField(max_length=255, db_index=True)
    path = models.JSONField() 
    length_km = models.DecimalField(max_digits=10, decimal_places=2)  # Use Decimal for better precision
    created_at = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False)  # For soft deletion

    def __str__(self):
        return f"{self.name} ({self.length_km} km)"

    class Meta:
        verbose_name = "Fiber Route"
        verbose_name_plural = "Fiber Routes"
        indexes = [
            models.Index(fields=['office', 'name']),
        ]



