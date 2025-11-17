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
from django.db import DatabaseError
from django.core.exceptions import ObjectDoesNotExist
import logging
from django.http import Http404
logger = logging.getLogger(__name__)

from django.db import transaction

class BaseAPIView(APIView):
    """
    Base API view to handle common response structures.
    """

    def success_response(self, message, data=None, status_code=status.HTTP_200_OK):
        return Response({"message": message,"data": data},status=status_code)

    def error_response(self, message, details=None, status_code=status.HTTP_400_BAD_REQUEST):
        return Response({"message": message,"details": details},status=status_code)
    
    def permission_check(self, staff_member):
        """Helper method to check if the staff member has 'admin' role."""
        if staff_member.role != "admin":
            return False, "Permission denied. Only admins can view or manage this data."
        return True, None


    def authentication(self, request):
        """
        Validates the JWT token passed in the Authorization header.
        Returns the decoded token or raises an error if invalid.
        """
        try:
            auth_user = request.headers.get('Authorization')
            if auth_user is None:
                return Response({"detail": "Authorization token is missing."}, status=401)
            
            try:
                decoded_token = jwt.decode(auth_user, settings.SECRET_KEY, algorithms=['HS256'])
                if 'id' not in decoded_token:
                    return Response({"detail": "Token has no id"}, status=status.HTTP_401_UNAUTHORIZED)
                return decoded_token
            except jwt.ExpiredSignatureError:
                return Response({"Token has expired."}, status=status.HTTP_401_UNAUTHORIZED)
            except jwt.InvalidTokenError:
                return Response({"Invalid token."}, status=status.HTTP_401_UNAUTHORIZED)
            
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

    class StaffLoginSerializer(serializers.Serializer):
        email = serializers.EmailField()
        password = serializers.CharField()

    def post(self, request):
        serializer = self.StaffLoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({"status": "error", "message": "Invalid input.", "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        email = serializer.validated_data['email']
        password = serializer.validated_data['password']

        try:
            staff = Staff.objects.get(email=email)
            if not staff.check_password(password):
                raise ValueError("Invalid credentials.")
        except (Staff.DoesNotExist, ValueError):
            return Response({"status": "error", "message": "Invalid credentials."}, status=status.HTTP_401_UNAUTHORIZED)

        expiration_time = datetime.utcnow() + timedelta(minutes=settings.JWT_EXPIRATION_MINUTES)
        user_token = {
            'id': staff.pk,
            'company': staff.company.pk,
            'name': staff.name,
            'exp': expiration_time,
            'iat': datetime.utcnow(),
        }
        token = jwt.encode(user_token, settings.SECRET_KEY, algorithm='HS256')

        return Response({
            "status": "success",
            "token": token,
            "name": staff.name,
        }, status=status.HTTP_200_OK)




class ListAllStaffByCompany(BaseAPIView):

    def authenticate_and_get_staff(self, request):
        """Helper method to authenticate and fetch staff member."""
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
        """Handles post request for creating staff under a company."""
        staff_member, error = self.authenticate_and_get_staff(request)
        if not staff_member:
            return Response({"status": "error", "message": error}, status=status.HTTP_400_BAD_REQUEST)

        # Check for admin role permission
        is_admin, permission_error = self.permission_check(staff_member)
        if not is_admin:
            return Response({"status": "error", "message": permission_error}, status=status.HTTP_403_FORBIDDEN)

        try:
            request.data['company'] = staff_member.company.pk
            serializer = StaffSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({"status": "success", "data": serializer.data}, status=status.HTTP_201_CREATED)
            else:
                return Response({"status": "error", "message": "Invalid input.", "errors": serializer.errors},
                                status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"status": "error", "message": f"An error occurred while creating staff: {str(e)}"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get(self, request):
        """Handles get request for fetching staff data under a company."""
        staff_member, error = self.authenticate_and_get_staff(request)
        if not staff_member:
            return Response({"status": "error", "message": error}, status=status.HTTP_400_BAD_REQUEST)

        # Check for admin role permission
        is_admin, permission_error = self.permission_check(staff_member)
        if not is_admin:
            return Response({"status": "error", "message": permission_error}, status=status.HTTP_403_FORBIDDEN)

        try:
            serializer = CompanyStaffSerializers(staff_member.company)
            return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"status": "error", "message": f"An error occurred while retrieving company staff: {str(e)}"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class EditStaffProfile(BaseAPIView):

    def get_authenticated_staff(self, request):
        """
        Encapsulate the logic to authenticate and fetch staff instance.
        """
        decoded_token = self.authentication(request)
        user_id = decoded_token.get('id')
        if not user_id:
            raise Exception("User ID not found in token.")

        try:
            return Staff.objects.get(id=user_id)
        except Staff.DoesNotExist:
            raise Http404("Staff not found")

    def get(self, request):
        try:
            staff_instance = self.get_authenticated_staff(request)
            serializer = StaffProfileSerializer(staff_instance)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Http404:
            return Response({"detail": "Staff not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        try:
            staff_instance = self.get_authenticated_staff(request)
            serializer = StaffProfileSerializer(staff_instance, data=request.data, partial=True)

            if serializer.is_valid():
                serializer.save()
                logger.info(f"Staff profile updated for {staff_instance.name}")
                return Response(serializer.data, status=status.HTTP_200_OK)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Http404:
            return Response({"detail": "Staff not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error updating profile: {str(e)}")
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)


    

class ChangePasswordView(EditStaffProfile):
    def post(self, request):
        staff_instance = self.get_authenticated_staff(request)
        user_id = staff_instance.id
        
        try:
            staff = Staff.objects.get(id=user_id)
        except Staff.DoesNotExist:
            return self.error_response("Staff not found.", status.HTTP_404_NOT_FOUND)

        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')

        if not old_password or not new_password:
            return self.error_response("Old and new passwords are required.", status.HTTP_400_BAD_REQUEST)

        if not staff.check_password(old_password):
            return self.error_response("Old password is incorrect.", status.HTTP_400_BAD_REQUEST)

        staff.password = make_password(new_password)
        staff.save()

        return self.success_response("Password changed successfully.", status_code=status.HTTP_200_OK)

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



