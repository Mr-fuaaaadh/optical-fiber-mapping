from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import NetworkDevice, DevicePort, Design, CouplerCalculation
from .serializers import NetworkDeviceSerializer, DevicePortSerializer, DevicePortViewSerializers, DesignSerializer, CouplerCalculationSerializer
from opticalfiber_app.views import BaseAPIView
from opticalfiber_app.models import Staff
from office.models import Office
from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError
from django.db import DatabaseError
from rest_framework.pagination import PageNumberPagination

class CustomPagination(PageNumberPagination):
    page_size = 50

class NetworkDeviceListCreateAPIView(BaseAPIView):
    """
    List all NetworkDevices or create a new one.
    Includes authentication, error handling, and related field optimization.
    """

    def get_authenticated_user(self, request):
        try:
            auth_user = self.authentication(request) 
            user_id = auth_user.get('id')
            if not user_id:
                return None, "Unauthorized access"

            staff_member = Staff.objects.select_related('company').get(pk=user_id)
            return staff_member, None

        except Staff.DoesNotExist:
            return None, "Staff member not found in the database."
        except Exception as e:
            return None, f"An error occurred while fetching staff details: {str(e)}"

    def get(self, request, *args, **kwargs):
        auth_user, error = self.get_authenticated_user(request)
        if error:
            return Response({"error": error}, status=status.HTTP_400_BAD_REQUEST)

        try:
            devices = NetworkDevice.objects.select_related('staff', 'office')\
                                        .filter(office__company=auth_user.company)\
                                        .order_by('id')

            paginator = CustomPagination()
            paginated_devices = paginator.paginate_queryset(devices, request)
            serializer = NetworkDeviceSerializer(paginated_devices, many=True)
            return paginator.get_paginated_response(serializer.data)

        except Exception as e:
            import traceback
            traceback.print_exc()
            return Response({"error": f"Failed to fetch devices: {str(e)}"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request, *args, **kwargs):
        auth_user, error = self.get_authenticated_user(request)
        if error:
            return Response({"error": error}, status=status.HTTP_400_BAD_REQUEST)

        try:
            request.data['staff'] = auth_user.pk
            serializer = NetworkDeviceSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({"error": f"Failed to create device: {str(e)}"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class NetworkDeviceRetrieveUpdateDestroyAPIView(NetworkDeviceListCreateAPIView):
    """
    Retrieve, update, or delete a specific NetworkDevice with authentication and error handling.
    """

    def get_object(self, pk):
        try:
            return NetworkDevice.objects.select_related('staff', 'office').get(pk=pk)
        except NetworkDevice.DoesNotExist:
            return None

    def handle_auth_and_get_object(self, request, pk):
        """Helper function to centralize auth + object retrieval logic"""
        user, error = self.get_authenticated_user(request)
        if error:
            return None, None, Response({"error": error}, status=status.HTTP_401_UNAUTHORIZED)

        device = self.get_object(pk)
        if device is None:
            return None, None, Response({"error": "Network device not found."}, status=status.HTTP_404_NOT_FOUND)
        
        return user, device, None

    def get(self, request, pk, *args, **kwargs):
        user, device, error_response = self.handle_auth_and_get_object(request, pk)
        if error_response:
            return error_response
        
        serializer = DevicePortViewSerializers(device)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk, *args, **kwargs):
        user, device, error_response = self.handle_auth_and_get_object(request, pk)
        if error_response:
            return error_response
        
        serializer = NetworkDeviceSerializer(device, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, *args, **kwargs):
        user, device, error_response = self.handle_auth_and_get_object(request, pk)
        if error_response:
            return error_response
        
        device.delete()
        return Response({"message": "Device deleted successfully."}, status=status.HTTP_204_NO_CONTENT)


class DevicePortListCreateAPIView(NetworkDeviceListCreateAPIView):
    """
    List all DevicePorts or create a new one.
    """

    def handle_auth_and_get_object(self, request, pk):
        """Helper function to centralize auth + object retrieval logic"""
        user, error = self.get_authenticated_user(request)
        if error:
            return None, None, Response({"error": error}, status=status.HTTP_401_UNAUTHORIZED)

        return user, None

    def get(self, request, device_id, *args, **kwargs):
        user, error = self.get_authenticated_user(request)
        if error:
            return Response({"error": error}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            device = get_object_or_404(NetworkDevice, pk=device_id)
            ports = DevicePort.objects.filter(device=device.pk)
            serializer = DevicePortSerializer(ports, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Office.DoesNotExist:
            return Response({"error": "Office not found."}, status=status.HTTP_404_NOT_FOUND)
        except DatabaseError:
            return Response({"error": "A database error occurred."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request, *args, **kwargs):
        user, error = self.get_authenticated_user(request)
        if error:
            return Response({"error": error}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            serializer = DevicePortSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response({"errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except ValidationError as ve:
            return Response({"error": str(ve)}, status=status.HTTP_400_BAD_REQUEST)
        except DatabaseError:
            return Response({"error": "A database error occurred while saving."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DevicePortRetrieveUpdateDestroyAPIView(NetworkDeviceListCreateAPIView):
    """
    Retrieve, update, or delete a specific DevicePort.
    """

    def handle_auth_and_get_object(self, request, pk):
        """Helper function to centralize auth + object retrieval logic"""
        user, error = self.get_authenticated_user(request)
        if error:
            return None, None, Response({"error": error}, status=status.HTTP_401_UNAUTHORIZED)

        # Retrieve the DevicePort object
        try:
            port = DevicePort.objects.get(pk=pk)
        except DevicePort.DoesNotExist:
            return user, None, Response({"error": "DevicePort not found"}, status=status.HTTP_404_NOT_FOUND)

        return user, port, None


    def get(self, request, pk, *args, **kwargs):
        user, port, error_response = self.handle_auth_and_get_object(request, pk)
        if error_response:
            return error_response

        serializer = DevicePortSerializer(port)
        return Response(serializer.data)

    def put(self, request, pk, *args, **kwargs):
        user, port, response = self.handle_auth_and_get_object(request, pk)
        if response:
            return response

        port = response
        serializer = DevicePortSerializer(port, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, *args, **kwargs):
        user, port, response = self.handle_auth_and_get_object(request, pk)
        if response:
            return response

        port = port
        port.delete()
        return Response(status=status.HTTP_200_OK)
    



class DesignListCreateAPIView(NetworkDeviceListCreateAPIView):
    """Create Design with multiple CouplerCalculations at the same time"""

    def post(self, request):
        staff, error = self.get_authenticated_user(request)
        if error:
            return Response({"error": error}, status=401)

        serializer = DesignSerializer(data=request.data, context={"company": staff.company})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

    def get(self, request):
        staff, error = self.get_authenticated_user(request)
        if error:
            return Response({"error": error}, status=401)

        designs = Design.objects.filter(company=staff.company)
        serializer = DesignSerializer(designs, many=True)
        return Response(serializer.data, status=200)
    


class DesignRetrieveUpdateDestroyAPIView(NetworkDeviceListCreateAPIView):
    """
    Retrieve, update, or delete a single Design and its nested CouplerCalculations
    for the logged-in user's company.
    """

    def get_authenticated_user(self, request):
        auth_user = self.authentication(request)
        user_id = auth_user.get("id")
        if not user_id:
            return None, "Unauthorized access"

        try:
            staff = Staff.objects.select_related("company").get(pk=user_id)
            return staff, None
        except Staff.DoesNotExist:
            return None, "Staff not found"

    def get_object(self, pk, company):
        try:
            return Design.objects.prefetch_related("couplers").get(
                pk=pk, company=company
            )
        except Design.DoesNotExist:
            return None

    def get(self, request, pk):
        user, error = self.get_authenticated_user(request)
        if error:
            return Response({"error": error}, status=status.HTTP_401_UNAUTHORIZED)

        design = self.get_object(pk, user.company)
        if not design:
            return Response(
                {"error": "Design not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = DesignSerializer(design)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        user, error = self.get_authenticated_user(request)
        if error:
            return Response({"error": error}, status=status.HTTP_401_UNAUTHORIZED)

        design = self.get_object(pk, user.company)
        if not design:
            return Response(
                {"error": "Design not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = DesignSerializer(
            design,
            data=request.data,
            context={"company": user.company}
        )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    def delete(self, request, pk):
        user, error = self.get_authenticated_user(request)
        if error:
            return Response({"error": error}, status=status.HTTP_401_UNAUTHORIZED)

        design = self.get_object(pk, user.company)
        if not design:
            return Response(
                {"error": "Design not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        design.delete()
        return Response(
            {"message": "Design deleted successfully"},
            status=status.HTTP_204_NO_CONTENT
        )
    
