from django.urls import path

from . import views
from .views import GoogleCheck, Register, PasswordResetAPIView, \
    PasswordResetConfirmAPIView, RegisterWithInvite, RegisterWithInvitePartner, \
    GetUserData  # Importiere die google_login-Methode
from .views import RefreshCustomerView
urlpatterns = [
    path('auth/google/', GoogleCheck.as_view(), name="GoogleCheck"),  # Definiere den Pfad für die google_login-Methode
    path('auth/register/', Register.as_view(),name="Register"),  # Definiere den Pfad für die Register-Methode

    path('auth/refresh-token/', RefreshCustomerView.as_view(), name='RefreshToken'),

    path('auth/get-userdata/', GetUserData.as_view(), name='GetUserData'),

    path('auth/register-invite-company/', RegisterWithInvite.as_view(), name='RegisterWithInvite'),
    path('auth/register-invite-partner/', RegisterWithInvitePartner.as_view(), name='RegisterWithInvitePartner'),

    path('auth/password-reset/', PasswordResetAPIView.as_view(), name='password_reset'),
    path('auth/password-reset-confirm/<uidb64>/<token>/', PasswordResetConfirmAPIView.as_view(), name='password_reset_confirm_api'),

    path('auth/login/', views.LoginViewNew.as_view(), name="GoogleCheck"),  # Definiere den Pfad für die google_login-Methode
]

#old login
#path('auth/login/', LoginView.as_view(), name="Login"),  # Definiere den Pfad für die Login-Methode