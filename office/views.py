from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from opticalfiber_app.views import BaseAPIView
from .serializers import OfficeSerializer
from opticalfiber_app.models import Company
from .models import Office
# Create your views here.


class OfficeView(BaseAPIView):
    def post(self,request):
        auth_user = self.authentication(request)
        if not auth_user:
            return Response({"error": "Authentication failed"}, status=status.HTTP_401_UNAUTHORIZED)
        
        request.data['company'] = user_id
    
        serializer = OfficeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"status": "success"}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        

        

