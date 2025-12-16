import logging
from django.db import DatabaseError
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework.exceptions import ValidationError as DRFValidationError
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.response import Response
from rest_framework import status
from opticalfiber_app.views import BaseAPIView
from .serializers import FiberRouteSerializer,FiberRouteWithTotalSerializer
from .models import FiberRoute
from .tasks import * 
from django.db.models import Prefetch
from django.shortcuts import get_object_or_404
from django.core.cache import cache
from office.models import Office
from rest_framework import status, generics


logger = logging.getLogger(__name__)

class FiberRouteCreateView(generics.CreateAPIView, BaseAPIView):
    """
    Create a new fiber route.
    """
    serializer_class = FiberRouteSerializer
    queryset = FiberRoute.objects.all()

    def create(self, request, *args, **kwargs):
        try:
            auth_user = self.authentication(request)
            if not auth_user:
                return self.error_response("Authentication failed", status.HTTP_401_UNAUTHORIZED)

            staff = get_object_or_404(Staff, pk=auth_user.get("id"))
            mutable_data = request.data.copy()
            mutable_data["created_by"] = staff.pk

            serializer = self.get_serializer(data=mutable_data)
            serializer.is_valid(raise_exception=True)

            # Perform save with model-level validation
            try:
                self.perform_create(serializer)
            except DjangoValidationError as e:
                return self.error_response(
                    message=" ".join(e.messages),
                    status_code=status.HTTP_400_BAD_REQUEST
                )

            return self.success_response(
                data=serializer.data,
                message="Fiber route has been created successfully.",
                status_code=status.HTTP_201_CREATED
            )

        except DRFValidationError as e:
            return Response({"message": e.detail}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return self.handle_exception(e)

    def perform_create(self, serializer):
        try:
            serializer.save()
        except DjangoValidationError as e:
            raise DRFValidationError(e.messages)



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

            serializer = FiberRouteWithTotalSerializer(fiber_routes, many=True)
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
            fiber_route = FiberRoute.objects.filter(pk=fiber_route_id, office__company_id=company_id).first()

            if not fiber_route:
                logger.warning("Fiber route ID %s not found or access denied for company %s", fiber_route_id, company_id)
                return Response(
                    {"error": "Fiber route not found or you do not have permission to delete it"},
                    status=status.HTTP_404_NOT_FOUND
                )

            fiber_route.delete()

            logger.info("Fiber route ID %s deleted by company %s", fiber_route_id, company_id)
            return Response(
                {"message": "Fiber route deleted successfully"},
                status=status.HTTP_204_NO_CONTENT
            )

        except DatabaseError as db_err:
            logger.error("Database error while deleting fiber route %s: %s", fiber_route_id, db_err)
            return Response(
                {"error": "A database error occurred"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        except Exception as e:
            logger.exception("Unexpected error deleting fiber route %s: %s", fiber_route_id, e)
            return Response(
                {"error": "An unexpected error occurred"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


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