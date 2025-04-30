from django.urls import path
from .views import *

urlpatterns = [
    path('register/', RegisterCompanyView.as_view(), name='register'),
    path('login/',CompanyStaffAuthenticationView.as_view(), name="login"),
    path('staffs/', ListAllStaffByCompany.as_view(),name="staffs"),
    path('update/user/profile/',EditStaffProfile.as_view(),name="edit_profile")
    
    
]