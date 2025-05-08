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
from django.core.cache import cache
from asgiref.sync import sync_to_async  # For async views
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

            # Validate before dispatching to Celery
            serializer = FiberRouteSerializer(data=request.data)
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
    def get(self, request):
        try:
            auth_user = self.authentication(request)
            if not auth_user:
                return self.error_response("Authentication failed", status.HTTP_401_UNAUTHORIZED)

            company_id = auth_user.get('company')
            if not company_id:
                return self.error_response("Company information missing", status.HTTP_400_BAD_REQUEST)

            # Try to get from cache
            cache_key = f"fiber_routes_company_{company_id}"
            cached_data = cache.get(cache_key)

            if cached_data:
                return Response(cached_data, status=status.HTTP_200_OK)

            # Not in cache → fetch from DB
            fiber_routes = FiberRoute.objects.filter(office__company__id=company_id)
            if not fiber_routes.exists():
                return self.error_response("No fiber routes found for this company", status.HTTP_404_NOT_FOUND)

            serializer = FiberRouteSerializer(fiber_routes, many=True)
            data = serializer.data

            # Set cache for 5 minutes
            cache.set(cache_key, data, timeout=300)

            return Response(data, status=status.HTTP_200_OK)

        except (ObjectDoesNotExist, DatabaseError, Exception) as e:
            logger.error(f"Error in FiberRouteListView: {str(e)}")
            return self.handle_exception(e)

        

class FiberRouteManagementView(BaseAPIView):
    def delete(self, request, route_id):
        try:
            auth_user = self.authentication(request)
            if not auth_user:
                return self.error_response("Authentication failed", status.HTTP_401_UNAUTHORIZED)

            company_id = auth_user.get('company')
            if not company_id:
                logger.warning("Company ID missing in authentication data")
                return self.error_response("Company information missing", status.HTTP_400_BAD_REQUEST)

            fiber_route = FiberRoute.objects.get(id=route_id, office__company__id=company_id)
            fiber_route.delete()
            return Response({"message": "Fiber route deleted successfully"}, status=status.HTTP_204_NO_CONTENT)

        except (ObjectDoesNotExist, DatabaseError, Exception) as e:
            return self.handle_exception(e)
        
    def put(self, request, route_id):
        try:
            auth_user = self.authentication(request)
            if not auth_user:
                return self.error_response("Authentication failed", status.HTTP_401_UNAUTHORIZED)

            company_id = auth_user.get('company')
            if not company_id:
                logger.warning("Company ID missing in authentication data")
                return self.error_response("Company information missing", status.HTTP_400_BAD_REQUEST)

            fiber_route = FiberRoute.objects.get(id=route_id, office__company__id=company_id)
            serializer = FiberRouteSerializer(fiber_route, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        except (ObjectDoesNotExist, DatabaseError, Exception) as e:
            return self.handle_exception(e)




        



    
