from django.db import models
from opticalfiber_app.models import Staff
from office.models import Office

# Create your models here.
class Customer(models.Model):
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE, related_name='customers')
    office = models.ForeignKey(Office, on_delete=models.CASCADE, related_name='customers')
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, unique=True)
    address = models.TextField()
    latitude = models.FloatField()
    longitude = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name