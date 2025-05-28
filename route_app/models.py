from office.models import Office
from django.db import models
from opticalfiber_app.models import *
from django.core.exceptions import ValidationError
from django.utils import timezone

class FiberRoute(models.Model):
    office = models.ForeignKey(Office, on_delete=models.CASCADE, related_name='fiber_routes', db_index=True)
    created_by = models.ForeignKey(Staff, on_delete=models.CASCADE, null=True, blank=True, related_name='fiber_routes_created')
    name = models.CharField(max_length=255, db_index=True)
    path = models.JSONField()
    length_km = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} ({self.length_km} km)"

    def clean(self):
        from payment_app.models import Payment

        company = self.office.company.pk
        total_km = FiberRoute.objects.filter(
            office__company=company,
            is_deleted=False
        ).exclude(pk=self.pk).aggregate(
            total=models.Sum('length_km')
        )['total'] or 0

        total_km += self.length_km

        print(f"DEBUG: Total fiber length (including current): {total_km} km")

        # Calculate how much km is beyond the first free 500 km
        paid_km = total_km - 500
        if paid_km <= 0:
            # still in free zone, no payment required
            return

        # Calculate how many 500 km chunks require payment
        required_chunks = int(paid_km // 500) + (1 if paid_km % 500 else 0)

        # Count how many payments have been made successfully
        paid_chunks = Payment.objects.filter(
            company=company,
            status='success',
            valid_until__gte=timezone.now()
        ).count()

        if required_chunks > paid_chunks:
            raise ValidationError(
                f"Fiber length limit exceeded. "
                f"Total fiber: {total_km} km. "
                f"Payment required for {required_chunks} chunks, "
                f"but only {paid_chunks} payments found."
            )



    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)




