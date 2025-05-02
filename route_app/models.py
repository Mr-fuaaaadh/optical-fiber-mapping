from office.models import Office
from django.db import models


class FiberRoute(models.Model):
    office = models.ForeignKey(Office, on_delete=models.CASCADE, related_name='fiber_routes')
    name = models.CharField(max_length=255)
    path = models.JSONField() 
    length_km = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.length_km} km)"

    class Meta:
        verbose_name = "Fiber Route"
        verbose_name_plural = "Fiber Routes"

