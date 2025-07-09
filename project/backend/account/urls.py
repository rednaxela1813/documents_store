# 📦 account/urls.py
from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import (
    RegisterUserView,
    UserMeView,
    SetPasswordView,
    PasswordResetRequestView,
    PasswordResetConfirmView,
    LogoutView
)

app_name = 'account'

urlpatterns = [
    path('register/', RegisterUserView.as_view(), name='register'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('me/', UserMeView.as_view(), name='me'),
    path('set_password/', SetPasswordView.as_view(), name='set_password'),
    path('password/reset/', PasswordResetRequestView.as_view(), name='password_reset_request'),
    path('password/reset/confirm/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('logout/', LogoutView.as_view(), name='logout'),
]
