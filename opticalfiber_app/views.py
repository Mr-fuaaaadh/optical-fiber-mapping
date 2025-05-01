from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from django.contrib.auth.hashers import make_password
from rest_framework_simplejwt.tokens import RefreshToken
from django.conf import settings
import jwt
from .serializers import *
from .models import Company, Staff, OTP
from datetime import timedelta, datetime
from django.shortcuts import get_object_or_404
from .utils import OTPService
from .tokens import get_tokens_for_user 

from django.db import transaction

class BaseAPIView(APIView):
    """
    Base API view to handle common response structures.
    """

    def success_response(self, message, data=None, status_code=status.HTTP_200_OK):
        return Response({"message": message,"data": data},status=status_code)

    def error_response(self, message, details=None, status_code=status.HTTP_400_BAD_REQUEST):
        return Response({"message": message,"details": details},status=status_code)
    

    def authentication(self, request):
        """
        Validates the JWT token passed in the Authorization header.
        Returns the decoded token or raises an error if invalid.
        """
        try:
            # Get the token from the Authorization header
            auth_user = request.headers.get('Authorization')
            if auth_user is None:
                return Response({"Authorization token is missing."}, status=status.HTTP_401_UNAUTHORIZED)
            
            # Remove the "Bearer " part from the token if it's there
            if auth_user.startswith("Bearer "):
                token = auth_user.split(" ")[1]  # Extract the token
            else:
                return Response({"Invalid token format. Expected Bearer token."}, status=status.HTTP_401_UNAUTHORIZED)

            # Decode the token
            try:
                decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
                return decoded_token  # Return decoded token if valid
            except jwt.ExpiredSignatureError:
                return Response({"Token has expired."})
            except jwt.InvalidTokenError:
                return Response({"Invalid token."})
            
        except Exception as e:
            return Response({f"Authentication failed: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class RegisterCompanyView(BaseAPIView):
    """
    API view to handle the registration of a new company and its admin staff.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        # Validate Admin Staff Inputs First
        admin_name = request.data.get('admin_name')
        admin_email = request.data.get('admin_email')
        admin_password = request.data.get('admin_password')

        if not (admin_name and admin_email and admin_password):
            return self.error_response(
                "Admin staff details are required before registering the company.",
                details={
                    "admin_name": "required",
                    "admin_email": "required",
                    "admin_password": "required"
                },
                status_code=status.HTTP_400_BAD_REQUEST
            )

        # Validate Company Inputs
        serializer = CompanySerializer(data=request.data)
        if not serializer.is_valid():
            return self.error_response(
                "Invalid company input.",
                details=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Using a transaction to ensure everything is saved together
            with transaction.atomic():
                # Save company data
                company = serializer.save()

                # Save admin staff after validating the company
                Staff.objects.create(
                    company=company,
                    name=admin_name,
                    email=admin_email,
                    password=make_password(admin_password),
                    role='admin',
                )

            return self.success_response(
                "Company and Admin Staff registered successfully!",
                data=serializer.data,
                status_code=status.HTTP_201_CREATED
            )

        except Exception as error:
            # In case of any exception, the transaction is rolled back, nothing is saved.
            return self.error_response(
                "An unexpected error occurred while registering company and admin.",
                details=str(error),
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class CompanyStaffAuthenticationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            email = request.data.get('email')
            password = request.data.get('password')

            if not email or not password:
                return Response({"status": "error", "message": "Email and password are required."}, status=status.HTTP_400_BAD_REQUEST)

            try:
                staff = Staff.objects.get(email=email)
            except Staff.DoesNotExist:
                return Response({"status": "error", "message": "Invalid credentials."}, status=status.HTTP_401_UNAUTHORIZED)

            if not staff.check_password(password):
                return Response({"status": "error", "message": "Invalid credentials."}, status=status.HTTP_401_UNAUTHORIZED)

            # Generate token with company_id inside
            token_data = get_tokens_for_user(staff)

            return Response({
                "status": "success",
                "message": "Login successful.",
                **token_data,
                "user": {
                    "id": staff.pk,
                    "name": staff.name,
                    "email": staff.email,
                    "role": staff.role,
                    "company_id": staff.company.pk,
                }
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"status": "error", "message": "Something went wrong.", "details": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class ListAllStaffByCompany(BaseAPIView):
    def get(self, request):
        try:
            auth_user = self.authentication(request)
            user_id = auth_user.get('user_id')

            if not user_id:
                return Response({"status": "error"},status=status.HTTP_400_BAD_REQUEST)

            staff_member = Staff.objects.select_related('company').get(pk=user_id)
            if staff_member.role == "admin":
                serializer = CompanyStaffSerializers(staff_member.company)
                return Response({"status": "success","data": serializer.data},status=status.HTTP_200_OK)
            else:
                return Response(
                    {"message": "Permission denied. Only admins can view this data."},status=status.HTTP_403_FORBIDDEN)
        except Staff.DoesNotExist:
            return Response({"status": "error"},status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"status": "error", "message": f"{str(e)}"},status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class EditStaffProfile(BaseAPIView):
    def put(self, request):
        # Get the authenticated user
        auth_user = self.authentication(request)
        
        # Get the staff ID (user_id) from the authenticated user
        staff_id = auth_user.get('user_id')
        if not staff_id:
            return Response({"detail": "User ID is missing"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Fetch the staff member by the authenticated user ID
            staff = Staff.objects.get(id=staff_id)
        except Staff.DoesNotExist:
            return Response({"detail": "Staff member not found"}, status=status.HTTP_404_NOT_FOUND)

        # Use the serializer to validate and update the staff data
        serializer = StaffSerializer(staff, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()  # Save the updated staff data
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        # If the serializer is not valid, return the validation errors
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


class ForgotPasswordView(BaseAPIView):
    def post(self, request):
        email = request.data.get('email')

        if not email:
            return self.error_response("Email is required.", status.HTTP_400_BAD_REQUEST)

        try:
            staff = Staff.objects.get(email=email, is_active=True)
        except Staff.DoesNotExist:
            return self.error_response("Email not found.", status.HTTP_404_NOT_FOUND)

        try:
            # Generate OTP
            otp_code = OTPService.generate_otp()

            # Save OTP to OTP model (automatically handles expiry)
            OTP.objects.create(
                email=email,
                otp=otp_code
                # expires_at is set automatically in OTP model's save()
            )

            # Send OTP via email
            OTPService.send_otp_email(staff.name, staff.email, otp_code)

        except Exception as e:
            return self.error_response(f"Failed to send OTP: {str(e)}", status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({
            "status": "success",
            "message": "OTP has been sent to your email."
        }, status=status.HTTP_200_OK)

    


class VerifyOTPView(BaseAPIView):
    def post(self, request):
        email = request.data.get('email')
        otp_code = request.data.get('otp')

        if not email or not otp_code:
            return self.error_response("Email and OTP are required.", status.HTTP_400_BAD_REQUEST)

        try:
            valid, message = OTPService.verify_otp(email, otp_code)

            if not valid:
                return self.error_response(message, status.HTTP_400_BAD_REQUEST)

            return Response({
                "status": "success",
                "message": message
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return self.error_response(f"An error occurred: {str(e)}", status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class ResetPasswordView(BaseAPIView):
    def post(self, request):
        email = request.data.get('email')
        new_password = request.data.get('new_password')

        if not email or not new_password:
            return self.error_response("Email and new password are required.", status.HTTP_400_BAD_REQUEST)

        try:
            staff = Staff.objects.get(email=email, is_active=True)
            staff.password = make_password(new_password)
            staff.save()

            return Response({
                "status": "success",
                "message": "Password reset successfully."
            }, status=status.HTTP_200_OK)

        except Staff.DoesNotExist:
            return self.error_response("Email not found.", status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return self.error_response(f"An error occurred: {str(e)}", status.HTTP_500_INTERNAL_SERVER_ERROR)
