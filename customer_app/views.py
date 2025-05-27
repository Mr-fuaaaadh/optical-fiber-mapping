from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.db import IntegrityError
from rest_framework.exceptions import ValidationError
from .models import Customer
from opticalfiber_app.views import BaseAPIView
from opticalfiber_app.models import Staff
from .serializers import CustomerSerializer
from office.models import Office

class CustomerAPIView(BaseAPIView):
    """
    API view to retrieve and create customers for the authenticated staff's office.
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
            return None, f"Authentication error: {str(e)}"

    def post(self, request):
        user, error = self.get_authenticated_user(request)
        if error:
            return Response({"error": error}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            data = request.data.copy()
            data['staff'] = user.pk

            serializer = CustomerSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except ValidationError as ve:
            return Response({"error": "Validation error", "details": ve.detail}, status=status.HTTP_400_BAD_REQUEST)
        except IntegrityError as ie:
            return Response({"error": "Database integrity error", "details": str(ie)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": f"Unexpected error: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class CustomerListView(CustomerAPIView):
    def get(self, request,office_id):
        user, error = self.get_authenticated_user(request)
        if error:
            return Response({"error": error}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            office = get_object_or_404(Office, pk=office_id)
            customers = Customer.objects.filter(office=office)
            serializer = CustomerSerializer(customers, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": f"Failed to retrieve customers: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CustomerManagementAPIView(CustomerAPIView):
    """
    API view to retrieve, update, or delete a specific customer by ID with staff validation.
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
            return None, f"Authentication error: {str(e)}"


    def get(self, request, customer_id):
        user, error = self.get_authenticated_user(request)
        if error:
            return Response({"error": error}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            customer = get_object_or_404(Customer, pk=customer_id)
            serializer = CustomerSerializer(customer)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except PermissionError as pe:
            return Response({"error": str(pe)}, status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            import traceback
            traceback.print_exc()  # Print full traceback to logs
            return Response(
                {"error": f"Failed to retrieve customer: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def put(self, request, customer_id):
        user, error = self.get_authenticated_user(request)
        if error:
            return Response({"error": error}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            customer = get_object_or_404(Customer, pk=customer_id)
            serializer = CustomerSerializer(customer, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except PermissionError as pe:
            return Response({"error": str(pe)}, status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return Response({"error": f"Failed to update customer: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, customer_id):
        user, error = self.get_authenticated_user(request)
        if error:
            return Response({"error": error}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            customer = get_object_or_404(Customer, pk=customer_id)
            customer.delete()
            return Response(status=status.HTTP_200_OK)
        except PermissionError as pe:
            return Response({"error": str(pe)}, status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return Response({"error": f"Failed to delete customer: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
