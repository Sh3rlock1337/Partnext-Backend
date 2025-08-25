from django.urls import path

from usermanager.views import ConfirmEmailView

from usermanager.views import ResendConfirmationMail

from usermanager.views import SetOperatingSystem

urlpatterns = [
    path("confirm-email/", ConfirmEmailView.as_view(), name="confirm-email"),
    path("resend-confirmation-email/", ResendConfirmationMail.as_view(), name="resend-confirmation-email"),
    path('set-os/', SetOperatingSystem.as_view(), name='set-os'),
]

