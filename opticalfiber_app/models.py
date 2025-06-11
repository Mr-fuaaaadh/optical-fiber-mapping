from django.db import models
from django.contrib.auth.hashers import make_password, check_password
from django.utils import timezone
from datetime import timedelta

class Company(models.Model):
    name = models.CharField(max_length=255, unique=True, db_index=True)
    registration_number = models.CharField(max_length=100, unique=True)
    logo = models.ImageField(upload_to='company_logos/', blank=True, null=True)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    address = models.TextField()
    website = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name
    

class Staff(models.Model):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('engineer', 'Engineer'),
    )

    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='staffs')
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)  # Store hashed password
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    profile_picture = models.ImageField(upload_to='staff_profiles/', blank=True, null=True)

    is_active = models.BooleanField(default=True)
    joined_on = models.DateField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Check if password is already hashed (optional safety)
        if not self.password.startswith('pbkdf2_'):  
            self.password = make_password(self.password)
        super(Staff, self).save(*args, **kwargs)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)

    def __str__(self):
        return f"{self.name} ({self.role})"
    


class OTP(models.Model):
    email = models.EmailField()
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    def is_valid(self):
        return timezone.now() < self.expires_at

    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(seconds=60)
        super().save(*args, **kwargs)