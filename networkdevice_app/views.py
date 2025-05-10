from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import NetworkDevice, DevicePort
from .serializers import NetworkDeviceSerializer, DevicePortSerializer
from opticalfiber_app.views import BaseAPIView
from opticalfiber_app.models import Staff
from office.models import Office
from django.shortcuts import get_object_or_404

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
                return None, "User ID is missing. Please provide a valid user ID."

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
            # Optional: filter devices by company
            devices = NetworkDevice.objects.select_related('staff', 'office')\
                                           .filter(office__company=auth_user.company)

            serializer = NetworkDeviceSerializer(devices, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
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
        
        serializer = NetworkDeviceSerializer(device)
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

    def get(self, request, *args, **kwargs):
        user, error = self.get_authenticated_user(request)
        if error:
            return Response({"error": error}, status=status.HTTP_401_UNAUTHORIZED)
        
        office_id = request.query_params.get('office')
        if not office_id:
            return Response({"error": "Office ID is required."}, status=status.HTTP_400_BAD_REQUEST)

        office = get_object_or_404(Office, id=office_id)
        if office:
            ports = DevicePort.objects.filter(device__office_id=office)
            serializer = DevicePortSerializer(ports, many=True)
            return Response(serializer.data)
        return Response({"error": "Office ID is required."}, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, *args, **kwargs):
        user, error = self.get_authenticated_user(request)
        if error:
            return Response({"error": error}, status=status.HTTP_401_UNAUTHORIZED)

        serializer = DevicePortSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(created_by=user)  # Set user as creator
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DevicePortRetrieveUpdateDestroyAPIView(NetworkDeviceListCreateAPIView):
    """
    Retrieve, update, or delete a specific DevicePort.
    """

    def handle_auth_and_get_object(self, request, pk):
        """Helper function to centralize auth + object retrieval logic"""
        user, error = self.get_authenticated_user(request)
        if error:
            return None, Response({"error": error}, status=status.HTTP_401_UNAUTHORIZED)

        # Retrieve the DevicePort object
        port = get_object_or_404(DevicePort, pk=pk)
        return user, port

    def get(self, request, pk, *args, **kwargs):
        user, response = self.handle_auth_and_get_object(request, pk)
        if response:
            return response

        serializer = DevicePortSerializer(response)
        return Response(serializer.data)

    def put(self, request, pk, *args, **kwargs):
        user, response = self.handle_auth_and_get_object(request, pk)
        if response:
            return response

        port = response
        serializer = DevicePortSerializer(port, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, *args, **kwargs):
        user, response = self.handle_auth_and_get_object(request, pk)
        if response:
            return response

        port = response
        port.delete()
        return Response(status=status.HTTP_200_OK)
    
