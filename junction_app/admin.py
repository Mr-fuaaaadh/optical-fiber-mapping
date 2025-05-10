from django.contrib import admin
from .models import JunctionBox, JunctionBoxDevice
# Register your models here.

admin.site.register(JunctionBox)
admin.site.register(JunctionBoxDevice)