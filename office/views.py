from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from opticalfiber_app.views import BaseAPIView
from .serializers import *
from opticalfiber_app.models import Company
from opticalfiber_app.models import Staff
from .models import Office
from django.http import Http404
import logging
from rest_framework.exceptions import ValidationError
from django.db import IntegrityError
logger = logging.getLogger(__name__)
# Create your views here.




class OfficeView(BaseAPIView):

    def _get_authenticated_user_and_company(self, request):
        auth_user = self.authentication(request)
        if not auth_user:
            return None, None, Response({"error": "Authentication failed"}, status=status.HTTP_401_UNAUTHORIZED)

        company_id = auth_user.get("company")
        if not company_id:
            return auth_user, None, Response({"error": "Company ID not found in authenticated user"}, status=status.HTTP_400_BAD_REQUEST)

        return auth_user, company_id, None

    def post(self, request):
        try:
            auth_user, company_id, error = self._get_authenticated_user_and_company(request)
            if error:
                return error

            company = get_object_or_404(Company, id=company_id)
            created_by = get_object_or_404(Staff, id=auth_user.get("id"))

            serializer = OfficeSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(company=company, created_by=created_by)

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except ValidationError as ve:
            return Response({"error": "Validation failed", "details": ve.detail}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.exception("Unexpected error during Office creation")
            return Response({"error": "An unexpected error occurred", "details": str(e)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get(self, request):
        try:
            auth_user, company_id, error = self._get_authenticated_user_and_company(request)
            if error:
                return error

            offices = Office.objects.filter(company__id=company_id)
            serializer = OfficeSerializer(offices, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": "An unexpected error occurred", "details": str(e)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    
        
class OfficeManagementView(BaseAPIView):

    def _get_authenticated_user_and_company(self, request):
        auth_user = self.authentication(request)
        if not auth_user:
            return None, None, Response({"error": "Authentication failed"}, status=status.HTTP_401_UNAUTHORIZED)

        company_id = auth_user.get('company')
        if not company_id:
            return auth_user, None, Response({"error": "Company ID not found in authenticated user"}, status=status.HTTP_400_BAD_REQUEST)

        return auth_user, company_id, None

    def _get_office(self, office_id, company_id):
        try:
            return Office.objects.get(id=office_id, company__id=company_id)
        except Office.DoesNotExist:
            raise Http404("Office not found")

    def get(self, request, office_id):
        try:
            auth_user, company_id, error = self._get_authenticated_user_and_company(request)
            if error:
                return error

            office = self._get_office(office_id, company_id)
            serializer = OfficeSerializer(office)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Http404 as e:
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": "An unexpected error occurred", "details": str(e)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request, office_id):
        try:
            auth_user, company_id, error = self._get_authenticated_user_and_company(request)
            if error:
                return error

            office = self._get_office(office_id, company_id)
            serializer = OfficeSerializer(office, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Http404 as e:
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": "An unexpected error occurred", "details": str(e)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, office_id):
        try:
            auth_user, company_id, error = self._get_authenticated_user_and_company(request)
            if error:
                return error

            office = self._get_office(office_id, company_id)
            office.delete()
            return Response({"message": "Office deleted successfully"}, status=status.HTTP_204_NO_CONTENT)

        except Http404 as e:
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": "An unexpected error occurred", "details": str(e)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        


# Branch View

class BranchView(BaseAPIView):

    def _get_authenticated_user(self, request):
        """Encapsulated logic to authenticate the user."""
        auth_user = self.authentication(request)
        if not auth_user:
            return None, self.error_response("Authentication failed", status.HTTP_401_UNAUTHORIZED)
        return auth_user, None

    def _get_company_id(self, auth_user):
        """Encapsulated logic to get the company ID from the user."""
        company_id = auth_user.get('company')
        if not company_id:
            return None, self.error_response("Company ID not found in authenticated user", status.HTTP_400_BAD_REQUEST)
        return company_id, None

    def post(self, request):
        try:
            auth_user, error = self._get_authenticated_user(request)
            if error:
                return error

            created_by = get_object_or_404(Staff, pk=auth_user.get('id'))
            serializer = BranchSerializer(data=request.data)
            if serializer.is_valid(raise_exception=True) :
                serializer.save(created_by=created_by)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except ValidationError as ve:
            return Response({"error": ve.detail}, status=status.HTTP_400_BAD_REQUEST)
        except IntegrityError as ie:
            return self.error_response("Database integrity error", status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return self.error_response("Unexpected error", status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get(self, request):
        try:
            auth_user, error = self._get_authenticated_user(request)
            if error:
                return error

            company_id, error = self._get_company_id(auth_user)
            if error:
                return error

            branches = Branch.objects.select_related('office').filter(office__company__id=company_id)
            if not branches.exists():
                return self.error_response("No branches found for this company", status.HTTP_404_NOT_FOUND)

            serializer = BranchSerializer(branches, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return self.error_response("Unexpected error", status.HTTP_500_INTERNAL_SERVER_ERROR)

    def _format_error(self, error):
        """Utility method to handle ValidationError formatting."""
        return error.detail if hasattr(error, 'detail') else str(error)

        

class BranchManagementView(BaseAPIView):
    def get_authenticated_user_and_branch(self, request, branch_id):
        auth_user = self.authentication(request)
        if not auth_user:
            return None, self.error_response("Authentication failed", status.HTTP_401_UNAUTHORIZED)

        company_id = auth_user.get('company')
        if not company_id:
            return None, self.error_response("Company ID not found in authenticated user", status.HTTP_400_BAD_REQUEST)

        try:
            branch = get_object_or_404(Branch, id=branch_id, office__company__id=company_id)
            return branch, None
        except Branch.DoesNotExist:
            return None, self.error_response("Branch not found", status.HTTP_404_NOT_FOUND)

    def delete(self, request, branch_id):
        branch, error_response = self.get_authenticated_user_and_branch(request, branch_id)
        if error_response:
            return error_response

        try:
            branch.delete()
            return Response({"message": "Branch deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return self.error_response("Unexpected error", status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request, branch_id):
        branch, error_response = self.get_authenticated_user_and_branch(request, branch_id)
        if error_response:
            return error_response

        try:
            serializer = BranchSerializer(branch, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return self.error_response("Unexpected error", status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get(self, request, branch_id):
        branch, error_response = self.get_authenticated_user_and_branch(request, branch_id)
        if error_response:
            return error_response

        try:
            serializer = BranchSerializer(branch)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return self.error_response("Unexpected error", status=status.HTTP_500_INTERNAL_SERVER_ERROR)
