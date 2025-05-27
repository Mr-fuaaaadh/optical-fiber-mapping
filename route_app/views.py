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
from office.models import Office

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
            staff =  get_object_or_404(Staff, pk=auth_user.get('id'))
            request.data['created_by'] = staff.pk
            
            serializer = FiberRouteSerializer(data=request.data)
            if serializer.is_valid():
                # Optionally, offload to background task using Celery
                serializer.save()  # Include creator info if needed
                return Response(
                    {"message": "Fiber route is being saved in the background."},
                    status=status.HTTP_202_ACCEPTED
                )
            else:
                return self.error_response(serializer.errors, status.HTTP_400_BAD_REQUEST)

        except (ValueError, DatabaseError, Exception) as e:
            return self.handle_exception(e)


    


class FiberRouteListView(BaseAPIView):
    """
    Retrieves a list of Fiber Routes for the authenticated user's company, using Redis cache.
    """
    def get(self, request, pk):
        try:
            # Authenticate user
            auth_user = self.authentication(request)
            if not auth_user:
                return self.error_response("Authentication failed", status.HTTP_401_UNAUTHORIZED)

            office = get_object_or_404(Office, pk=pk)
            if not office:
                return self.error_response("office information missing", status.HTTP_400_BAD_REQUEST)

            # Fetch from DB if not cached
            fiber_routes = FiberRoute.objects.filter(office=office)
            if not fiber_routes.exists():
                return self.error_response("No fiber routes found for this company", status.HTTP_404_NOT_FOUND)

            serializer = FiberRouteSerializer(fiber_routes, many=True)
            serialized_data = serializer.data

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