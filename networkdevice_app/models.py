from django.db import models
from opticalfiber_app.models import Staff
from office.models import Office
from django.utils import timezone


DEVICE_TYPES = [
    ('OLT', 'OLT'),
    ('ONT', 'ONT'),
    ('Splitter', 'Splitter'),
    ('Coupler', 'Coupler'),
    ('Transceiver', 'Transceiver'),
    ('Patch Panel', 'Patch Panel'),
    ('Optical Switch', 'Optical Switch'),
    ('Media Converter', 'Media Converter'),
    ('Network Interface Card (NIC)', 'Network Interface Card (NIC)'),
    ('Router', 'Router'),
    ('Switch', 'Switch'),
    ('Firewall', 'Firewall'),
]
class NetworkDevice(models.Model):
    """
    Model representing a network device.
    """
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE, verbose_name="Staff Member")
    office = models.ForeignKey(Office, on_delete=models.CASCADE, verbose_name="Office")
    device_type = models.CharField(max_length=50, choices=DEVICE_TYPES, verbose_name="Device Type")
    model_name = models.CharField(max_length=255, verbose_name="Model Name")
    description = models.TextField(null=True, blank=True, verbose_name="Device Description")
    ratio = models.CharField(max_length=10, null=True, blank=True, verbose_name="Splitter/Coupler Ratio")
    max_speed = models.IntegerField(null=True, blank=True, verbose_name="Maximum Speed (Mbps or Gbps)")
    color_coding = models.CharField(max_length=100, null=True, blank=True, verbose_name="Fiber Color Coding")
    insertion_loss = models.FloatField(null=True, blank=True, verbose_name="Insertion Loss (dB)")
    return_loss = models.FloatField(null=True, blank=True, verbose_name="Return Loss (dB)")
    port_count = models.IntegerField(null=True, blank=True, verbose_name="Number of Ports")
    supported_protocols = models.CharField(max_length=255, null=True, blank=True, verbose_name="Supported Protocols")
    latitude = models.FloatField()
    logitutde =  models.FloatField()

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated At")

    def __str__(self):
        return f"{self.device_type} - {self.model_name} ({self.color_coding})"


class DevicePort(models.Model):
    device = models.ForeignKey(NetworkDevice, related_name="ports", on_delete=models.CASCADE, verbose_name="Device")
    port_number = models.IntegerField(verbose_name="Port Number")
    port_type = models.CharField(max_length=50, choices=[('SFP', 'SFP'), ('Ethernet', 'Ethernet'), ('QSFP', 'QSFP')], verbose_name="Port Type")
    speed = models.CharField(max_length=100, verbose_name="Port Speed (Gbps)", null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated At")

    def __str__(self):
        return f"Port {self.port_number} - {self.device} ({self.port_type})"

