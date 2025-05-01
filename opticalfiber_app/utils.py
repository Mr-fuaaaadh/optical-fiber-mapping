import random
from datetime import datetime, timedelta
from django.conf import settings
from django.core.mail import send_mail
from .models import OTP



class OTPService:
    @staticmethod
    def generate_otp(length=6):
        """Generates a random numeric OTP of specified length."""
        return ''.join(str(random.randint(0, 9)) for _ in range(length))

    @staticmethod
    def send_otp_email(name, email, otp):
        """Sends an OTP email to the specified address."""
        subject = 'Password Reset OTP'
        message = (
            f'Hi {name},\n\n'
            f'Your One-Time Password (OTP) for password reset is: {otp}\n'
            'Please use it within 10 minutes.\n\n'
            'If you did not request this, please ignore this email.\n\n'
            'Regards,\nYour Support Team'
        )
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email])


    @staticmethod
    def verify_otp(email, otp_code):
        try:
            otp = OTP.objects.get(email=email, otp=otp_code)

            if not otp.is_valid():
                return False, "OTP has expired."

            return True, "OTP verified successfully."

        except OTP.DoesNotExist:
            return False, "Invalid OTP."