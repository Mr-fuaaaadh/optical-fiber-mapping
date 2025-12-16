from django.urls import path
from .views import *

urlpatterns = [
    path('register/', RegisterCompanyView.as_view(), name='register'),
    path('login/',CompanyStaffAuthenticationView.as_view(), name="login"),
    path('company/staffs/', ListAllStaffByCompany.as_view(),name="staffs"),
    path('update/user/profile/',EditStaffProfile.as_view(),name="edit_profile"),

    path('forgot/password/',ForgotPasswordView.as_view(),name="forgot_password"),
    path('verify/otp/',VerifyOTPView.as_view(),name="verify_otp"),
    path('reset/password/',ResetPasswordView.as_view(),name="reset_password"),
    path('change/password/', ChangePasswordView.as_view(), name='change_password'),



    
]