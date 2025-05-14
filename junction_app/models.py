from django.db import models
from opticalfiber_app.models import Staff
from office.models import Office
from networkdevice_app.models import NetworkDevice

class JunctionBox(models.Model):
    """
    Represents a junction box (either main or child).
    """
    office = models.ForeignKey(Office, on_delete=models.CASCADE, verbose_name="Office", related_name="junction_boxes")
    name = models.CharField(max_length=255, verbose_name="Junction Box Name")
    latitude = models.FloatField()
    longitude = models.FloatField()
    post_code = models.CharField(max_length=10, verbose_name="Post Code")
    description = models.TextField(null=True, blank=True, verbose_name="Description")
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE,  verbose_name="Staff Member")
    junction_type = models.CharField(max_length=50, choices=[('Main', 'Main'), ('Child', 'Child')], default='Child', verbose_name="Junction Box Type")

    def __str__(self):
        return f"{self.name} - {self.junction_type}"


class JunctionBoxDevice(models.Model):
    """
    Represents a device added to a junction box (splitter, coupler, etc.).
    """
    junction_box = models.ForeignKey(JunctionBox, related_name="devices", on_delete=models.CASCADE, verbose_name="Junction Box",)
    device = models.ForeignKey(NetworkDevice, related_name="junction_boxes", on_delete=models.CASCADE, verbose_name="Network Device")
    installation_date = models.DateField(null=True, blank=True, verbose_name="Installation Date")

    def __str__(self):
        return f"{self.device} added to {self.junction_box.name}"
