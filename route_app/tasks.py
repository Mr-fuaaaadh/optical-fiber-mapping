from django.core.cache import cache
from celery import shared_task
from django.db import DatabaseError
from .serializers import FiberRouteSerializer
import logging

logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=3)
def save_fiber_route_task(self, data, user_id=None):
    try:
        # Serializer validation and saving of fiber route
        serializer = FiberRouteSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        fiber_route = serializer.save(created_by_id=user_id)

        # Invalidate Redis cache for the company
        company_id = fiber_route.office.company.id
        cache_key = f"fiber_routes_company_{company_id}"
        cache.delete(cache_key)

        logger.info("Fiber route saved successfully and cache invalidated.")
    except Exception as e:
        logger.error(f"Error in Celery fiber save task: {str(e)}")
        raise self.retry(exc=e, countdown=5)  # Retry on failure
