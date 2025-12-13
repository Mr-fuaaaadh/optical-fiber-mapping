from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import FiberRoute
from django.core.cache import cache

def clear_fiber_routes_cache(office_id):
    cache_key = f"fiber_routes_office_{office_id}"
    cache.delete(cache_key)

@receiver(post_save, sender=FiberRoute)
def fiber_route_saved(sender, instance, **kwargs):
    clear_fiber_routes_cache(instance.office_id)

@receiver(post_delete, sender=FiberRoute)
def fiber_route_deleted(sender, instance, **kwargs):
    clear_fiber_routes_cache(instance.office_id)
