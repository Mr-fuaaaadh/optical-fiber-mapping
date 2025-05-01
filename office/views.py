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
    def post(self, request):
        try:
            auth_user = self.authentication(request)
            if not auth_user:
                return Response({"error": "Authentication failed"}, status=status.HTTP_401_UNAUTHORIZED)

            company_id = auth_user.get('company_id')
            if not company_id:
                return Response({"error": "Company ID not found in authenticated user"}, status=status.HTTP_400_BAD_REQUEST)

            company = Company.objects.get(id=company_id)

            serializer = OfficeSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(company=company)  # Injecting the company

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Company.DoesNotExist:
            return Response({"error": "Company not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response(
                {"error": "An unexpected error occurred", "details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        

    def get(self, request):
        try:
            auth_user = self.authentication(request)
            if not auth_user:
                return Response({"error": "Authentication failed"}, status=status.HTTP_401_UNAUTHORIZED)

            company_id = auth_user.get('company_id')
            if not company_id:
                return Response({"error": "Company ID not found in authenticated user"}, status=status.HTTP_400_BAD_REQUEST)

            offices = Office.objects.filter(company__id=company_id)
            serializer = OfficeSerializer(offices, many=True)

            return Response(serializer.data, status=status.HTTP_200_OK)

        except Company.DoesNotExist:
            return Response({"error": "Company not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response(
                {"error": "An unexpected error occurred", "details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
        
class OfficeManagementView(BaseAPIView):
    def delete(self, request, office_id):
        try:
            auth_user = self.authentication(request)
            if not auth_user:
                return Response({"error": "Authentication failed"}, status=status.HTTP_401_UNAUTHORIZED)

            company_id = auth_user.get('company_id')
            if not company_id:
                return Response({"error": "Company ID not found in authenticated user"}, status=status.HTTP_400_BAD_REQUEST)

            office = Office.objects.get(id=office_id, company__id=company_id)
            office.delete()

            return Response({"message": "Office deleted successfully"}, status=status.HTTP_204_NO_CONTENT)

        except Office.DoesNotExist:
            return Response({"error": "Office not found"}, status=status.HTTP_404_NOT_FOUND)
        except Company.DoesNotExist:
            return Response({"error": "Company not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response(
                {"error": "An unexpected error occurred", "details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        

    def put(self, request, office_id):
        try:
            auth_user = self.authentication(request)
            if not auth_user:
                return Response({"error": "Authentication failed"}, status=status.HTTP_401_UNAUTHORIZED)

            company_id = auth_user.get('company_id')
            if not company_id:
                return Response({"error": "Company ID not found in authenticated user"}, status=status.HTTP_400_BAD_REQUEST)

            office = Office.objects.get(id=office_id, company__id=company_id)
            serializer = OfficeSerializer(office, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()

            return Response(serializer.data, status=status.HTTP_200_OK)

        except Office.DoesNotExist:
            return Response({"error": "Office not found"}, status=status.HTTP_404_NOT_FOUND)
        except Company.DoesNotExist:
            return Response({"error": "Company not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response(
                {"error": "An unexpected error occurred", "details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
    def get(self, request, office_id):
        try:
            auth_user = self.authentication(request)
            if not auth_user:
                return Response({"error": "Authentication failed"}, status=status.HTTP_401_UNAUTHORIZED)

            company_id = auth_user.get('company_id')
            if not company_id:
                return Response({"error": "Company ID not found in authenticated user"}, status=status.HTTP_400_BAD_REQUEST)

            office = Office.objects.get(id=office_id, company__id=company_id)
            serializer = OfficeSerializer(office)

            return Response(serializer.data, status=status.HTTP_200_OK)

        except Office.DoesNotExist:
            return Response({"error": "Office not found"}, status=status.HTTP_404_NOT_FOUND)
        except Company.DoesNotExist:
            return Response({"error": "Company not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response(
                {"error": "An unexpected error occurred", "details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        

