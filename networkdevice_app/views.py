from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import NetworkDevice, DevicePort
from .serializers import NetworkDeviceSerializer, DevicePortSerializer

class NetworkDeviceListCreateAPIView(APIView):
    """
    List all NetworkDevices or create a new one.
    """
    def get(self, request, *args, **kwargs):
        devices = NetworkDevice.objects.all()
        serializer = NetworkDeviceSerializer(devices, many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        serializer = NetworkDeviceSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class NetworkDeviceRetrieveUpdateDestroyAPIView(APIView):
    """
    Retrieve, update, or delete a specific NetworkDevice.
    """
    def get_object(self, pk):
        try:
            return NetworkDevice.objects.get(pk=pk)
        except NetworkDevice.DoesNotExist:
            return None

    def get(self, request, pk, *args, **kwargs):
        device = self.get_object(pk)
        if device is None:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = NetworkDeviceSerializer(device)
        return Response(serializer.data)

    def put(self, request, pk, *args, **kwargs):
        device = self.get_object(pk)
        if device is None:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = NetworkDeviceSerializer(device, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, *args, **kwargs):
        device = self.get_object(pk)
        if device is None:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        device.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class DevicePortListCreateAPIView(APIView):
    """
    List all DevicePorts or create a new one.
    """
    def get(self, request, *args, **kwargs):
        ports = DevicePort.objects.all()
        serializer = DevicePortSerializer(ports, many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        serializer = DevicePortSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DevicePortRetrieveUpdateDestroyAPIView(APIView):
    """
    Retrieve, update, or delete a specific DevicePort.
    """
    def get_object(self, pk):
        try:
            return DevicePort.objects.get(pk=pk)
        except DevicePort.DoesNotExist:
            return None

    def get(self, request, pk, *args, **kwargs):
        port = self.get_object(pk)
        if port is None:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = DevicePortSerializer(port)
        return Response(serializer.data)

    def put(self, request, pk, *args, **kwargs):
        port = self.get_object(pk)
        if port is None:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = DevicePortSerializer(port, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, *args, **kwargs):
        port = self.get_object(pk)
        if port is None:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        port.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
