from django.db import models
from opticalfiber_app.models import Company, Staff
# Create your models here.

class Office(models.Model):

    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='offices')
    created_by = models.ForeignKey(Staff, on_delete=models.CASCADE, null=True, blank=True, related_name='offices_created')
    name = models.CharField(max_length=255)
    latitude = models.FloatField()
    longitude = models.FloatField()
    address = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    note = models.TextField(blank=True, null=True)


    def __str__(self):
        return f"{self.name} - {self.company.name}"

    class Meta:
        verbose_name = 'Office'
        verbose_name_plural = 'Offices'



class Branch(models.Model):
    office = models.ForeignKey(Office, related_name='branches', on_delete=models.CASCADE)
    created_by = models.ForeignKey(Staff, on_delete=models.CASCADE, null=True, blank=True, related_name='branches_created')
    name = models.CharField(max_length=255)
    logitude = models.FloatField()
    latitude = models.FloatField()
    address = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Branch'
        verbose_name_plural = 'Branches'
        ordering = ['created_at']



















