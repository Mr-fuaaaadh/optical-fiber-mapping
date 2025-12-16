import random
from datetime import timedelta
from django.utils import timezone
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
        subject = "Password Reset OTP"
        message = (
            f"Hi {name},\n\n"
            f"Your One-Time Password (OTP) for password reset is: {otp}\n"
            "This OTP will expire in 10 minutes.\n\n"
            "If you did not request this, please ignore this email.\n\n"
            "Regards,\n"
            "Corus InfoTech Team"
        )

        # Send email, explicitly fail if sending fails
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=False
        )

    @staticmethod
    def verify_otp(email, otp_code):
        """
        Verify OTP for a given email.
        Returns tuple: (bool: success, str: message)
        """
        try:
            otp = OTP.objects.get(email=email, otp=otp_code)

            if not otp.is_valid():
                otp.delete()  # Remove expired OTP
                return False, "OTP has expired."

            otp.delete()  # Delete OTP after successful verification
            return True, "OTP verified successfully."

        except OTP.DoesNotExist:
            return False, "Invalid OTP."
