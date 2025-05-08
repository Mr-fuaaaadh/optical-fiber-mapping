from office.models import Office
from django.db import models
from opticalfiber_app.models import Staff  
from django.utils.text import slugify
from decimal import Decimal

class FiberRoute(models.Model):
    office = models.ForeignKey(Office, on_delete=models.CASCADE, related_name='fiber_routes', db_index=True)
    name = models.CharField(max_length=255, db_index=True)
    slug = models.SlugField(unique=True, blank=True)
    path = models.JSONField() 
    length_km = models.DecimalField(max_digits=10, decimal_places=2)  # Use Decimal for better precision
    created_by = models.ForeignKey(Staff, on_delete=models.CASCADE, null=True, blank=True, related_name='fiber_routes_created')
    created_at = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False)  # For soft deletion

    def __str__(self):
        return f"{self.name} ({self.length_km} km)"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_path_length(self):
        """
        Example method that calculates the length of the route based on path coordinates
        (Placeholder for actual path calculation logic).
        """
        path = self.path
        if isinstance(path, list) and len(path) > 1:
            return sum([calculate_distance(p1, p2) for p1, p2 in zip(path[:-1], path[1:])])
        return Decimal(0)

    class Meta:
        verbose_name = "Fiber Route"
        verbose_name_plural = "Fiber Routes"
        indexes = [
            models.Index(fields=['office', 'name']),
        ]



