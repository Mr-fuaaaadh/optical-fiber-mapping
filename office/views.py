from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from opticalfiber_app.views import BaseAPIView
from .serializers import *
from opticalfiber_app.models import Company
from .models import Office
import logging

logger = logging.getLogger(__name__)
# Create your views here.

from rest_framework.exceptions import ValidationError
from django.db import IntegrityError

class OfficeView(BaseAPIView):
    def post(self, request):
        try:
            auth_user = self.authentication(request)
            if not auth_user:
                return Response({"error": "Authentication failed"}, status=status.HTTP_401_UNAUTHORIZED)

            company_id = auth_user.get('company')
            if not company_id:
                return Response({"error": "Company ID not found in authenticated user"}, status=status.HTTP_400_BAD_REQUEST)

            company = Company.objects.get(id=company_id)

            serializer = OfficeSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(company=company)

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Company.DoesNotExist:
            return Response({"error": "Company not found"}, status=status.HTTP_404_NOT_FOUND)

        except ValidationError as ve:
            return Response({"error": "Validation failed", "details": ve.detail}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            logger.exception("Unexpected error during Office creation")
            return Response(
                {"error": "An unexpected error occurred", "details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        

    def get(self, request):
        try:
            auth_user = self.authentication(request)
            if not auth_user:
                return Response({"error": "Authentication failed"}, status=status.HTTP_401_UNAUTHORIZED)

            company_id = auth_user.get('company')
            if not company_id:
                return Response({"error": "Company ID not found in authenticated user"}, status=status.HTTP_400_BAD_REQUEST)

            offices = Office.objects.filter(company__id=company_id)
            serializer = OfficeSerializer(offices, many=True)

            return Response(serializer.data, status=status.HTTP_200_OK)

        except Company.DoesNotExist:
            return Response({"error": "Company not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": "An unexpected error occurred", "details": str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
        
class OfficeManagementView(BaseAPIView):
    def delete(self, request, office_id):
        try:
            auth_user = self.authentication(request)
            if not auth_user:
                return Response({"error": "Authentication failed"}, status=status.HTTP_401_UNAUTHORIZED)

            company_id = auth_user.get('company')
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
            return Response({"error": "An unexpected error occurred", "details": str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

    def put(self, request, office_id):
        try:
            auth_user = self.authentication(request)
            if not auth_user:
                return Response({"error": "Authentication failed"}, status=status.HTTP_401_UNAUTHORIZED)

            company_id = auth_user.get('company')
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

            company_id = auth_user.get('company')
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
            return Response({"error": "An unexpected error occurred", "details": str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        


# Branch View

class BranchView(BaseAPIView):
    def post(self, request):
        try:
            # Authenticate user
            auth_user = self.authentication(request)
            if not auth_user:
                return self.error_response("Authentication failed", status.HTTP_401_UNAUTHORIZED)

            # Validate office_id presence
            office_id = request.data.get('office_id')
            if not office_id:
                return self.error_response("Office ID is required", status.HTTP_400_BAD_REQUEST)

            # Fetch the office object
            try:
                office = get_object_or_404(Office, id=office_id)
            except Office.DoesNotExist:
                return self.error_response("Office not found", status.HTTP_404_NOT_FOUND)

            # Validate and save the branch data
            serializer = BranchSerializer(data=request.data)
            try:
                serializer.is_valid(raise_exception=True)
                serializer.save(office=office)
            except ValidationError as ve:
                return self.error_response("Validation error", status.HTTP_400_BAD_REQUEST, details=ve.detail)

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except ValidationError as ve:
            return self.error_response("Validation error", status.HTTP_400_BAD_REQUEST, details=ve.detail)
        except IntegrityError as ie:
            return self.error_response("Database integrity error", status.HTTP_400_BAD_REQUEST, details=str(ie))
        except Exception as e:
            return self.error_response("Unexpected error", status.HTTP_500_INTERNAL_SERVER_ERROR, details=str(e))
        


    def get(self, request):
        try:
            auth_user = self.authentication(request)
            if not auth_user:
                return self.error_response("Authentication failed", status.HTTP_401_UNAUTHORIZED)

            company_id = auth_user.get('company')
            if not company_id:
                return self.error_response("Company ID not found in authenticated user", status.HTTP_400_BAD_REQUEST)

            # Optimized query: prefetch related office to reduce DB hits
            branches = Branch.objects.select_related('office').filter(office__company__id=company_id)

            if not branches.exists():
                return self.error_response("No branches found for this company", status.HTTP_404_NOT_FOUND)

            serializer = BranchSerializer(branches, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return self.error_response("Unexpected error", status.HTTP_500_INTERNAL_SERVER_ERROR, details=str(e))

        

class BranchManagementView(BaseAPIView):
    def delete(self, request, branch_id):
        try:
            auth_user = self.authentication(request)
            if not auth_user:
                return self.error_response("Authentication failed", status.HTTP_401_UNAUTHORIZED)

            company_id = auth_user.get('company')
            if not company_id:
                return self.error_response("Company ID not found in authenticated user", status.HTTP_400_BAD_REQUEST)

            # Fetch the branch object
            branch = get_object_or_404(Branch, id=branch_id, office__company__id=company_id)
            branch.delete()

            return Response({"message": "Branch deleted successfully"}, status=status.HTTP_204_NO_CONTENT)

        except Branch.DoesNotExist:
            return self.error_response("Branch not found", status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return self.error_response("Unexpected error", status.HTTP_500_INTERNAL_SERVER_ERROR, details=str(e))
        
    def put(self, request, branch_id):
        try:
            auth_user = self.authentication(request)
            if not auth_user:
                return self.error_response("Authentication failed", status.HTTP_401_UNAUTHORIZED)

            company_id = auth_user.get('company')
            if not company_id:
                return self.error_response("Company ID not found in authenticated user", status.HTTP_400_BAD_REQUEST)

            # Fetch the branch object
            branch = get_object_or_404(Branch, id=branch_id, office__company__id=company_id)
            serializer = BranchSerializer(branch, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()

            return Response(serializer.data, status=status.HTTP_200_OK)

        except Branch.DoesNotExist:
            return self.error_response("Branch not found", status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return self.error_response("Unexpected error", status=status.HTTP_500_INTERNAL_SERVER_ERROR, details=str(e))