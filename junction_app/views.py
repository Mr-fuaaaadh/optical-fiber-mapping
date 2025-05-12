from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import JunctionBox, JunctionBoxDevice
from .serializers import JunctionBoxSerializer, JunctionDeviceSerializer
from opticalfiber_app.views import BaseAPIView
from opticalfiber_app.models import Staff

class JunctionAPIView(BaseAPIView):
    """
    Handles the creation and retrieval of Junctions.
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

    def post(self, request):
        try:
            auth_user, error = self.get_authenticated_user(request)
            if error:
                return Response({"error": error}, status=status.HTTP_400_BAD_REQUEST)

            # Ensure request.data is mutable before updating
            data = request.data.copy()
            data['staff'] = auth_user.pk

            serializer = JunctionBoxSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get(self, request):
        auth_user, error = self.get_authenticated_user(request)
        if error:
            return Response({"error": error}, status=status.HTTP_400_BAD_REQUEST)
        try:
            # Optional: Filter by staff's company if needed
            junctions = JunctionBox.objects.filter(office__company=auth_user.company).all()
            serializer = JunctionBoxSerializer(junctions, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        


class JunctionDetailAPIView(BaseAPIView):
    """
    Handles the retrieval, update, and deletion of a specific Junction.
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
        
    def get(self, request, pk):
        auth_user, error = self.get_authenticated_user(request)
        if error:
            return Response({"error": error}, status=status.HTTP_400_BAD_REQUEST)
        try:
            junction = get_object_or_404(JunctionBox, pk=pk)
            serializer = JunctionBoxSerializer(junction)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    def put(self, request, pk):
        auth_user, error = self.get_authenticated_user(request)
        if error:
            return Response({"error": error}, status=status.HTTP_400_BAD_REQUEST)
        try:
            junction = get_object_or_404(JunctionBox, pk=pk)
            serializer = JunctionBoxSerializer(junction, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    def delete(self, request, pk):
        auth_user, error = self.get_authenticated_user(request)
        if error:
            return Response({"error": error}, status=status.HTTP_400_BAD_REQUEST)
        try:
            junction = get_object_or_404(JunctionBox, pk=pk)
            junction.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




class JunctionDeviceAPIView(BaseAPIView):
    """
    Handles the creation and retrieval of Junction Devices.
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
        
    def post(self, request,pk):
        auth_user, error = self.get_authenticated_user(request)
        if error:
            return Response({"error": error}, status=status.HTTP_400_BAD_REQUEST)
        try:
            serializer = JunctionDeviceSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

    def get(self, request):
        auth_user, error = self.get_authenticated_user(request)
        if error:
            return Response({"error": error}, status=status.HTTP_400_BAD_REQUEST)
        try:
            junction_devices = JunctionBoxDevice.objects.filter(junction_box__office__company=auth_user.company).all()
            serializer = JunctionDeviceSerializer(junction_devices, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class JunctionDeviceDetailAPIView(BaseAPIView):
    """
    Handles the retrieval, update, and deletion of a specific Junction Device.
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
        
    def get(self, request, pk):
        auth_user, error = self.get_authenticated_user(request)
        if error:
            return Response({"error": error}, status=status.HTTP_400_BAD_REQUEST)
        try:
            junction_device = get_object_or_404(JunctionBoxDevice, pk=pk)
            serializer = JunctionDeviceSerializer(junction_device)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

    def put(self, request, pk):
        auth_user, error = self.get_authenticated_user(request)
        if error:
            return Response({"error": error}, status=status.HTTP_400_BAD_REQUEST)
        try:
            junction_device = get_object_or_404(JunctionBoxDevice, pk=pk)
            serializer = JunctionDeviceSerializer(junction_device, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    def delete(self, request, pk):
        auth_user, error = self.get_authenticated_user(request)
        if error:
            return Response({"error": error}, status=status.HTTP_400_BAD_REQUEST)
        try:
            junction_device = get_object_or_404(JunctionBoxDevice, pk=pk)
            junction_device.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)