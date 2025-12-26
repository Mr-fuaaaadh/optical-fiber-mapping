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
        from decimal import Decimal

        company = self.office.company.pk

        total_km = FiberRoute.objects.filter(
            office__company=company,
            is_deleted=False
        ).exclude(pk=self.pk).aggregate(
            total=models.Sum('length_km')
        )['total'] or 0

        total_km = Decimal(total_km) + Decimal(self.length_km)

        # Calculate how much km is beyond the first free 50 km
        free_limit = Decimal('50')
        paid_km = total_km - free_limit

        if paid_km <= 0:
            # Just reached the 50 km limit?
            if total_km == free_limit:
                raise ValidationError(
                    f"You have now reached the 50 km free fiber route limit. "
                    f"Any further addition will require payment."
                )
            # Still under free limit — allow
            return

        # Now check if enough payments are made
        required_chunks = int(paid_km // 50) + (1 if paid_km % 50 else 0)

        paid_chunks = Payment.objects.filter(
            company=company,
            status='success',
            valid_until__gte=timezone.now()
        ).count()

        if required_chunks > paid_chunks:
            raise ValidationError(
                f"Fiber length limit exceeded. "
                # f"Free limit: 50 km. Payment required for {required_chunks} chunk(s) "
                # f"({required_chunks * 50 + 50} km total), but only {paid_chunks} payment(s) found."
            )


    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)




