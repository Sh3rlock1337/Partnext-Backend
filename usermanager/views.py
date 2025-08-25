from django.shortcuts import render
from rest_framework import permissions, status
from rest_framework.views import APIView

from usermanager.models import UserSettings
from rest_framework.response import Response

from simpleapi.views import language_manager

from protocoll.models import Protocol


# Create your views here.

class ConfirmEmailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        if request.user.is_authenticated:
            preferred_language = UserSettings.objects.get(customer_user=request.user).preferred_language
            protocol = Protocol.objects.create(
                user=request.user,
                action='OTHER',
                related_object='UserSettings'
            )
            try:
                usersettings = UserSettings.objects.get(customer_user=request.user)

                if usersettings.email_verified:
                    email_already_confirmed = language_manager.get_text(preferred_language, 'email_already_confirmed')
                    protocol.description = email_already_confirmed
                    protocol.save()
                    return Response({'message': email_already_confirmed}, status=status.HTTP_400_BAD_REQUEST)

                # Überprüfen, ob die OTP im request.data vorhanden ist
                if 'otp' not in request.data:
                    email_otp_required = language_manager.get_text(preferred_language, 'email_otp_required')
                    protocol.description = email_otp_required
                    protocol.save()

                    return Response({'message': email_otp_required}, status=status.HTTP_400_BAD_REQUEST)

                # Überprüfen, ob die OTP numerisch ist
                otp = request.data['otp']
                if not otp.isdigit():
                    email_top_numberic_error = language_manager.get_text(preferred_language, 'email_otp_numeric_error')
                    protocol.description = email_top_numberic_error
                    protocol.save()
                    return Response({'message': email_top_numberic_error}, status=status.HTTP_400_BAD_REQUEST)

                # Überprüfen, ob die OTP korrekt ist
                if int(otp) == usersettings.otp:
                    usersettings.email_verified = True
                    usersettings.save()

                    email_successful_confirmed = language_manager.get_text(preferred_language, 'email_successful_confirmed')
                    protocol.action = 'UPDATE'
                    protocol.description = email_successful_confirmed
                    protocol.save()
                    return Response({'message': email_successful_confirmed}, status=status.HTTP_200_OK)
                else:
                    email_invalid_otp = language_manager.get_text(preferred_language, 'email_invalid_otp')
                    protocol.description = email_invalid_otp
                    protocol.save()
                    return Response({'message': email_invalid_otp}, status=status.HTTP_400_BAD_REQUEST)

            except UserSettings.DoesNotExist:

                return Response({"error": "UserSettings not found"}, status=status.HTTP_404_NOT_FOUND)

        return Response({'message': 'You are not authenticated'}, status=status.HTTP_401_UNAUTHORIZED)

class ResendConfirmationMail(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def post(self, request):
        if request.user.is_authenticated:
            try:
                protocol = Protocol.objects.create(
                    user=request.user,
                    action='OTHER',
                    related_object='UserSettings'
                )
                usersettings = UserSettings.objects.get(customer_user=request.user)
                if usersettings.email_verified:
                    email_already_confirmed = language_manager.get_text(usersettings.preferred_language, 'email_already_confirmed')
                    protocol.description = email_already_confirmed
                    protocol.save()
                    return Response({'message': email_already_confirmed}, status=status.HTTP_400_BAD_REQUEST)

                #send mail
                print("EMAIL SENDEN", usersettings.otp)
                email_successful_send = language_manager.get_text(usersettings.preferred_language, 'email_successful_send')
                protocol.action = 'CREATE'
                protocol.description = email_successful_send
                protocol.save()
                return Response({'message': email_successful_send}, status=status.HTTP_200_OK)

            except UserSettings.DoesNotExist:
                return Response({"error": "UserSettings not found"}, status=status.HTTP_404_NOT_FOUND)

        return Response({'message': 'You are not authenticated'}, status=status.HTTP_401_UNAUTHORIZED)


class SetOperatingSystem(APIView):
    permissions_classes = [permissions.IsAuthenticated]

    def post(self, request):
        if request.user.is_authenticated:
            try:
                usersettings = UserSettings.objects.get(customer_user=request.user)
                usersettings.os = request.data['os']
                usersettings.save()
                return Response({'message': 'OS set'}, status=status.HTTP_200_OK)
            except UserSettings.DoesNotExist:
                return Response({"error": "UserSettings not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response({'message': 'You are not authenticated'}, status=status.HTTP_401_UNAUTHORIZED)
