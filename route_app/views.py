import logging
from django.db import DatabaseError
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.response import Response
from rest_framework import status
from opticalfiber_app.views import BaseAPIView
from .serializers import FiberRouteSerializer
from .models import FiberRoute
from .tasks import * 
from django.db.models import Prefetch
from django.shortcuts import get_object_or_404
from django.core.cache import cache

logger = logging.getLogger(__name__)

class FiberRouteView(BaseAPIView):
    """
    Handles the creation of a new Fiber Route.
    """
    def post(self, request):
        try:
            auth_user = self.authentication(request)
            if not auth_user:
                return self.error_response("Authentication failed", status.HTTP_401_UNAUTHORIZED)

            # Include the authenticated user in the serializer context for validation
            serializer = FiberRouteSerializer(data=request.data, context={'request': request})
            serializer.is_valid(raise_exception=True)

            # Dispatch to Celery
            save_fiber_route_task.delay(request.data, auth_user.get('id'))

            return Response({"message": "Fiber route is being saved in the background."},
                            status=status.HTTP_202_ACCEPTED)

        except (ValueError, DatabaseError, Exception) as e:
            return self.handle_exception(e)


    


class FiberRouteListView(BaseAPIView):
    """
    Retrieves a list of Fiber Routes for the authenticated user's company, using Redis cache.
    """

    CACHE_TIMEOUT = 300  # 5 minutes

    def get(self, request):
        try:
            # Authenticate user
            auth_user = self.authentication(request)
            if not auth_user:
                return self.error_response("Authentication failed", status.HTTP_401_UNAUTHORIZED)

            company_id = auth_user.get('company')
            if not company_id:
                return self.error_response("Company information missing", status.HTTP_400_BAD_REQUEST)

            cache_key = f"fiber_routes_company_{company_id}"
            cached_data = cache.get(cache_key)

            if cached_data:
                return Response(cached_data, status=status.HTTP_200_OK)

            # Fetch from DB if not cached
            fiber_routes = FiberRoute.objects.filter(office__company__id=company_id)
            if not fiber_routes.exists():
                return self.error_response("No fiber routes found for this company", status.HTTP_404_NOT_FOUND)

            serializer = FiberRouteSerializer(fiber_routes, many=True)
            serialized_data = serializer.data

            # Store in cache
            cache.set(cache_key, serialized_data, timeout=self.CACHE_TIMEOUT)

            return Response(serialized_data, status=status.HTTP_200_OK)

        except (ObjectDoesNotExist, DatabaseError) as e:
            logger.exception("Database-related error in FiberRouteListView")
            return self.error_response("A database error occurred", status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            logger.exception("Unexpected error in FiberRouteListView")
            return self.error_response("An unexpected error occurred", status.HTTP_500_INTERNAL_SERVER_ERROR)
        


class FiberRouteManagementView(BaseAPIView):

    def _get_authenticated_company(self, request):
        """Authenticate user and return company ID or error response"""
        user = self.authentication(request)
        if not user:
            return None, self.error_response("Authentication failed", status.HTTP_401_UNAUTHORIZED)

        company_id = user.get("company")
        if not company_id:
            logger.warning("Company ID missing in authentication data for user: %s", user.get("id"))
            return None, self.error_response("Company information missing", status.HTTP_400_BAD_REQUEST)

        return company_id, None

    def delete(self, request, fiber_route_id):
        company_id, error_response = self._get_authenticated_company(request)
        if error_response:
            return error_response

        try:
            fiber_route = get_object_or_404(FiberRoute, id=fiber_route_id, office__company_id=company_id)
            fiber_route.delete()

            logger.info("Fiber route ID %s deleted by company %s", fiber_route_id, company_id)
            return Response({"message": "Fiber route deleted successfully"}, status=status.HTTP_204_NO_CONTENT)

        except DatabaseError as db_err:
            logger.error("Database error while deleting fiber route %s: %s", fiber_route_id, db_err)
            return self.error_response("A database error occurred", status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            logger.exception("Unexpected error deleting fiber route %s: %s", fiber_route_id, e)
            return self.error_response("An unexpected error occurred", status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request, fiber_route_id):
        company_id, error_response = self._get_authenticated_company(request)
        if error_response:
            return error_response

        try:
            fiber_route = get_object_or_404(FiberRoute, id=fiber_route_id, office__company_id=company_id)

            serializer = FiberRouteSerializer(fiber_route, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()

            logger.info("Fiber route ID %s updated by company %s", fiber_route_id, company_id)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except DatabaseError as db_err:
            logger.error("Database error while updating fiber route %s: %s", fiber_route_id, db_err)
            return self.error_response("A database error occurred", status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            logger.exception("Unexpected error updating fiber route %s: %s", fiber_route_id, e)
            return self.error_response("An unexpected error occurred", status.HTTP_500_INTERNAL_SERVER_ERROR)




        



    
