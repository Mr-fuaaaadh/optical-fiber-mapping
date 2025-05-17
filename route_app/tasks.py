from django.core.cache import cache
from celery import shared_task
from django.shortcuts import get_object_or_404
from opticalfiber_app.models import Staff
from .serializers import FiberRouteSerializer
import logging

logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=3)
def save_fiber_route_task(self, data, user_id):
    try:
        logger.info("Running save_fiber_route_task...")

        user = get_object_or_404(Staff, id=user_id)
        logger.info(f"Found user: {user}")

        serializer = FiberRouteSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        logger.info(f"Serializer valid with data: {serializer.validated_data}")

        fiber_route = serializer.save(created_by_id=user.pk)
        logger.info(f"Saved FiberRoute with ID: {fiber_route.id}")

        # Invalidate Redis cache
        company_id = fiber_route.office.company.id
        cache_key = f"fiber_routes_company_{company_id}"
        cache.delete(cache_key)

        logger.info(f"Fiber route saved by user {user.id} and cache invalidated for company {company_id}.")

    except Exception as e:
        logger.error(f"Error in save_fiber_route_task: {str(e)}")
        raise self.retry(exc=e, countdown=5)

