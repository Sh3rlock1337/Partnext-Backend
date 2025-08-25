import hashlib
import json
import uuid
from datetime import timedelta

from django.http import HttpResponse, JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.debug import sensitive_post_parameters
from django.views.generic import FormView, View
from django_ratelimit.decorators import ratelimit
from oauth2_provider.signals import app_authorized

from django.db import models


from django.contrib.auth import authenticate
from django.utils import timezone
from allauth.socialaccount.models import SocialApp, SocialToken, SocialAccount
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from oauth2_provider.oauth2_validators import RefreshToken
from oauth2_provider.views.mixins import OAuthLibMixin
from oauthlib.common import generate_token
from django.contrib.auth.models import User, Group
from rest_framework import generics, permissions
from oauth2_provider.models import AccessToken, Application, get_access_token_model
from oauth2_provider.contrib.rest_framework import TokenHasReadWriteScope, TokenHasScope
from google.auth.transport import requests
from google.oauth2 import id_token
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core.mail import send_mail
from django.conf import settings
from simpleapi.serializers import UserSerializer

from utils.passwordManager.createRndmPassword import createRndmPassword
from utils.languageManager.language import LanguageManager

from usermanager.models import UserSettings

from utils.permissionsManager.permissions import generate_jwt

from utils.emailManager.numberGenerator import generate_otp

from company.models import Company

from protocoll.models import Protocol

from company.models import InvitationCompany

from company.models import InvitationPartnerToCreate

from partner.models import Partner

from partner.models import InvitationPartner

language_manager = LanguageManager()

# Create your views here.
class UserList(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated, TokenHasReadWriteScope]
    queryset = User.objects.all()
    serializer_class = UserSerializer

def create_token_for_user(user):
    expires = timezone.now() + timedelta(days=1)
    expires_refresh = timezone.now() + timedelta(days=2)
    # Lösche alte Tokens
    AccessToken.objects.filter(user=user).delete()
    RefreshToken.objects.filter(user=user).delete()

    # Hol die OAuth2-Anwendung
    application = Application.objects.get(
        name='normal oauth')  # Stelle sicher, dass du die richtige Anwendung verwendest

    # Erstelle neuen AccessToken
    access_token = AccessToken.objects.create(
        user=user,
        token=generate_token(),
        expires=expires,
        scope="read write",
        application=application  # Anwendung hinzufügen
    )

    # Erstelle neuen RefreshToken
    refresh_token = RefreshToken.objects.create(
        user=user,
        token=generate_token(),
        access_token=access_token,
        application=application  # Anwendung hinzufügen
    )
    refresh_token.save()
    return access_token.token, refresh_token.token


class GoogleCheck(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        token = request.data.get('token')
        if not token:
            return Response({'message': 'Token fehlt'}, status=400)

        try:
            idinfo = id_token.verify_oauth2_token(token, requests.Request(), '1080992180160-8snc8hhij1vkqme1fvqa8b46pc9c1km4.apps.googleusercontent.com')
            user_id = idinfo['sub']
            email = idinfo['email']
            name = idinfo['name']
            iss = idinfo['iss']
            azp = idinfo['azp']
            aud = idinfo['aud']
            email_verified = idinfo['email_verified']
            nbf = idinfo['nbf']
            picture = idinfo['picture']
            given_name = idinfo['given_name']
            iat = idinfo['iat']
            exp = idinfo['exp']
            jti = idinfo['jti']
            try:
                family_name = idinfo['family_name']
            except:
                family_name = ''



            # Finde oder erstelle den User
            try:
                if User.objects.filter(email=email).exists():
                    user = User.objects.get(email=email)
                    return Response({'message': 'This Email is already registered'}, status=400)
            except:
                pass

            user, created = User.objects.get_or_create(username=email, email=email, first_name=given_name, last_name=family_name, is_active=True)
            password = createRndmPassword()
            print("EMAIL SENDEN", password)


            user.set_password(password)
            user.save()
            UserSettings.objects.create(customer_user=user, email_verified=True)

            # Finde oder erstelle die SocialApp
            app, created = SocialApp.objects.get_or_create(provider='google')
            # Finde oder erstelle das SocialAccount
            social_account, created = SocialAccount.objects.get_or_create(
                user=user,
                provider='google',
                uid=user_id
            )

            expires_at = timezone.now() + timedelta(days=1)  # Token 24 Stunden gültig
            # Prüfe, ob es bereits einen SocialToken gibt
            try:
                social_token = SocialToken.objects.get(app=app, account=social_account)
                # Falls ein Token existiert, aktualisiere es
                social_token.token = token
                social_token.save()
            except SocialToken.DoesNotExist:
                # Falls kein Token existiert, erstelle einen neuen
                social_token = SocialToken.objects.create(
                    app=app,
                    account=social_account,
                    token=token
                )
            try:
                access_token, refresh_token = create_token_for_user(user)
            except:
                return Response({'message': 'OAuth2 Application nicht gefunden'}, status=400)
            print(access_token)
            return Response({
                'message': 'Registrierung erfolgreich',
                'access_token': str(access_token),
                'refresh_token': str(refresh_token),
                'permissions': generate_jwt(user)
            }, status=200)
        except ValueError:
            return Response({'message': 'Register not successful'}, status=400)



class Register(APIView):
    permission_classes = [permissions.AllowAny]

    @method_decorator(ratelimit(key='ip', rate='7/h', method='POST'))
    def post(self, request):
        print(request.data)


        try:
            checkforuser = User.objects.get(email=request.data.get('email'))
            print(checkforuser)
            if checkforuser:
                return Response({'message': 'This Email is already registered'}, status=400)

        except:
            pass

        email = request.data.get('email')
        password = request.data.get('password')
        username = request.data.get('email')
        first_name = request.data.get('first_name')
        last_name = request.data.get('last_name')
        user, created = User.objects.get_or_create(username=username, email=email, first_name=first_name, last_name=last_name)
        user.set_password(password)
        user.save()
        otp = generate_otp()
        UserSettings.objects.create(customer_user=user, otp=otp)
        #send mail
        print("EMAIL SENDEN", otp)
        access_token, refresh_token = create_token_for_user(user)

        preferred_language = UserSettings.objects.get(customer_user=user).preferred_language

        success_message = language_manager.get_text(preferred_language, 'success_login')
        return Response({
            'message': success_message,
            'access_token': str(access_token),
            'refresh_token': str(refresh_token),
            'permissions': generate_jwt(user)
        }, status=200)



class PasswordResetAPIView(GenericAPIView):
    permission_classes = [permissions.AllowAny]

    @method_decorator(ratelimit(key='ip', rate='4/h', method='POST'))
    def post(self, request):
        email = request.data.get('email')
        if not User.objects.filter(email=email).exists():
            return Response({"message": "User with this email does not exist."}, status=status.HTTP_400_BAD_REQUEST)


        user = User.objects.get(email=email)
        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        reset_url = f"http://localhost:3000/password-reset-confirm/{uidb64}/{token}/"  # Anpassung auf deine Frontend-URL

        send_mail(
            subject="Password Reset Request",
            message=f"Click the link to reset your password: {reset_url}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
        )
        preferred_language = UserSettings.objects.get(customer_user=user).preferred_language
        password_reset_send = language_manager.get_text(preferred_language, 'password_reset_send')
        Protocol.objects.create(
            user=user,
            action='OTHER',
            description='Password Reset Request',
            related_object='User'
        )

        return Response({"message": password_reset_send}, status=status.HTTP_200_OK)



class PasswordResetConfirmAPIView(GenericAPIView):
    permission_classes = [permissions.AllowAny]

    @method_decorator(ratelimit(key='user_or_ip', rate='4/m', method='POST'))
    def post(self, request, uidb64, token):
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and default_token_generator.check_token(user, token):
            new_password = request.data.get('new_password')
            user.set_password(new_password)
            user.save()

            preferred_language = UserSettings.objects.get(customer_user=user).preferred_language
            password_reset_successfull_message = language_manager.get_text(preferred_language, 'password_reset_success')
            Protocol.objects.create(
                user=user,
                action='OTHER',
                description='Password Reset Successfull',
                related_object='User'
            )
            return Response({"message": password_reset_successfull_message}, status=status.HTTP_200_OK)

        return Response({"message": "Invalid token or user."}, status=status.HTTP_400_BAD_REQUEST)



class RegisterWithInvite(APIView):
    permission_classes = [permissions.AllowAny]

    @method_decorator(ratelimit(key='ip', rate='4/h', method='POST'))

    def post(self, request):
        print(request.data)
        if not request.data.get('invite'):
            return Response({'message': 'Invite invalid'}, status=400)
        token = request.data.get('invite')
        try:
            invitation = InvitationCompany.objects.get(token=token, is_used=False)
        except:
            return Response({'message': 'Invite invalid'}, status=400)

        try:
            checkforuser = User.objects.get(email=request.data.get('email'))
            print(checkforuser)
            if checkforuser:
                return Response({'message': 'This Email is already registered'}, status=400)

        except:
            pass

        email = request.data.get('email')
        password = request.data.get('password')
        username = request.data.get('email')
        first_name = request.data.get('first_name')
        last_name = request.data.get('last_name')
        user, created = User.objects.get_or_create(username=username, email=email, first_name=first_name,
                                                   last_name=last_name)
        user.set_password(password)
        user.save()
        UserSettings.objects.create(customer_user=user, email_verified=True, is_invited_user_company=True, is_company_owner=False)

        access_token, refresh_token = create_token_for_user(user)

        preferred_language = UserSettings.objects.get(customer_user=user).preferred_language

        success_message = language_manager.get_text(preferred_language, 'success_login')

        #get the inviter company and add the user to the company
        company = invitation.company
        company.members.add(user)
        company.save()

        invitation.company_used_by = user
        invitation.is_used = True
        invitation.save()
        return Response({
            'message': success_message,
            'access_token': str(access_token),
            'refresh_token': str(refresh_token),
            'permissions': generate_jwt(user)


        }, status=200)



@method_decorator(csrf_exempt, name="dispatch")
class LoginViewNew(OAuthLibMixin, View):
    """
    Implements an endpoint to provide access tokens

    The endpoint is used in the following flows:
    * Authorization code
    * Password
    * Client credentials
    """

    @method_decorator(sensitive_post_parameters("password"))
    def post(self, request, *args, **kwargs):
        # Erstelle den neuen Token
        print(request.body)
        url, headers, body, status = self.create_token_response(request)
        if status == 200:
            access_token = json.loads(body).get("access_token")
            if access_token is not None:
                token_checksum = hashlib.sha256(access_token.encode("utf-8")).hexdigest()
                token_model = get_access_token_model()
                token = token_model.objects.get(token_checksum=token_checksum)
                refresh = RefreshToken.objects.get(access_token=token)
                # Benutzer aus dem Token ermitteln
                user = token.user

                # Lösche alle alten Access Tokens und zugehörigen Refresh Tokens für diesen Benutzer
                token_model.objects.filter(user=user).exclude(id=token.id).delete()
                RefreshToken.objects.filter(user=user).exclude(id=refresh.id).delete()

                # Benutzername oder andere Informationen ausgeben
                print(f"Eingeloggter Benutzer: {user.username}")
                try:
                    company = Company.objects.get(
                        models.Q(owner=user) |
                        models.Q(staff=user)
                    )
                    print("Firma gefunden")
                    if company.blocked:
                        print("Firma ist blockiert")
                        preferred_language = UserSettings.objects.get(customer_user=user).preferred_language
                        company_blocked = language_manager.get_text(preferred_language, 'company_blocked')
                        return JsonResponse({'message': company_blocked}, status=400)

                except Company.DoesNotExist:
                    pass




                # Benutzername oder andere Informationen ausgeben
                try:
                    partner = Partner.objects.get(
                        models.Q(partner_owner=user) |
                        models.Q(partner_staff=user)
                    )
                    print("Partner gefunden")
                    if partner.partner_blocked:
                        print("Partner ist blockiert")
                        preferred_language = UserSettings.objects.get(customer_user=user).preferred_language
                        partner_blocked = language_manager.get_text(preferred_language, 'partner_blocked')
                        return JsonResponse({'message': partner_blocked}, status=400)
                    else:
                        print("Partner ist nicht blockiert")
                except Partner.DoesNotExist:
                    pass

                # Body von JSON-String in Dictionary umwandeln
                body_dict = json.loads(body)
                # Berechtigungen hinzufügen
                body_dict['permissions'] = generate_jwt(user)

                # Zurück in JSON konvertieren
                body = json.dumps(body_dict)

                app_authorized.send(sender=self, request=request, token=token)



        response = HttpResponse(content=body, status=status)

        for k, v in headers.items():
            response[k] = v
        return response


class RegisterWithInvitePartner(APIView):
    permission_classes = [permissions.AllowAny]

    @method_decorator(ratelimit(key='ip', rate='4/h', method='POST'))
    def post(self, request):
        if not request.data.get('invite'):
            return Response({'message': 'Invite invalid'}, status=400)
        token = request.data.get('invite')
        try:
            invitation = InvitationPartnerToCreate.objects.get(token=token, is_used=False)


        except:
            try:

                invitation = InvitationPartner.objects.get(token=token, is_used=False)

            except:

                return Response({'message': 'Invite ss invalid'}, status=400)

        try:
            checkforuser = User.objects.get(email=request.data.get('email'))
            print(checkforuser)
            if checkforuser:
                return Response({'message': 'This Email is already registered'}, status=400)

        except:
            pass





        email = request.data.get('email')
        password = request.data.get('password')
        username = request.data.get('email')
        first_name = request.data.get('first_name')
        last_name = request.data.get('last_name')
        user, created = User.objects.get_or_create(username=username, email=email, first_name=first_name,
                                                   last_name=last_name)
        user.set_password(password)
        user.save()
        UserSettings.objects.create(customer_user=user, email_verified=True, is_invited_user_company=False,
                                    is_company_owner=False, is_invited_user_partner=True)

        #user partner hinzufügen und company owner auf false setzen
        try:
            partner = Partner.objects.get(id=invitation.partner.id)
            print(partner)
            partner.partner_staff.add(user)
            partner.save()
        except:
            print("kein invitaion.partner")
            print(invitation)
            pass

        access_token, refresh_token = create_token_for_user(user)

        preferred_language = UserSettings.objects.get(customer_user=user).preferred_language

        success_message = language_manager.get_text(preferred_language, 'success_login')

        # get the inviter company and add the user to the company

        invitation.partner_to_create_used_by = user
        invitation.is_used = True
        invitation.save()
        return Response({
            'message': success_message,
            'access_token': str(access_token),
            'refresh_token': str(refresh_token),
            'permissions': generate_jwt(user)

        }, status=200)


class GetUserData(APIView):
    permissions_classes = [permissions.IsAuthenticated]

    @method_decorator(ratelimit(key='get:username', rate='5/s', method='GET'))
    def get(self, request):
        if request.user.is_authenticated:
            user_data = request.user
            usersettings = UserSettings.objects.get(customer_user=user_data)

            return Response({'user_data': {'first_name': user_data.first_name, 'last_name': user_data.last_name,
                                           'email':user_data.email, 'is_staff':user_data.is_staff,
                                           'is_superuser':user_data.is_superuser, 'is_active':user_data.is_active}
                             , 'usersettings': {'email_verified': usersettings.email_verified, 'is_company_owner': usersettings.is_company_owner,
                                                'is_invited_user_company':usersettings.is_invited_user_company, 'is_invited_user_partner':usersettings.is_invited_user_partner,
                                                'preffered_language': usersettings.preferred_language, 'os': usersettings.os}}, status=200)
        else:
            return Response({'message': 'Not authenticated'}, status=400)




class RefreshCustomerView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):

        try:
            access_token = AccessToken.objects.get(token=request.data.get('access_token'))
        except AccessToken.DoesNotExist:
            return Response({'message': 'Access Token invalid'}, status=400)

        if access_token.is_expired():  # Check if the access token is expired
            access_token.delete()
            try:
                refresh_token = RefreshToken.objects.get(token=request.data.get('refresh_token'))
            except RefreshToken.DoesNotExist:
                return Response({'message': 'Refresh Token invalid'}, status=400)

            if not refresh_token.revoked:  # Check if refresh token is not revoked
                user = refresh_token.user
                access_token, refresh_token = create_token_for_user(user)  # Generate new tokens
                return Response({
                    'access_token': str(access_token)

                }, status=200)
            else:
                return Response({'message': 'Refresh Token revoked'}, status=400)
        else:

            return Response({'access_token': str(access_token)}, status=200)

#old login
#class LoginView(APIView):
#    permission_classes = [permissions.AllowAny]
#    def post(self, request):



 #       email = request.data.get('email')
  #      password = request.data.get('password')
   #     try:
#            user = User.objects.get(email=email)
   #     except User.DoesNotExist:
   #         return Response({'message': 'Ein Nutzer mit dieser Email existiert nicht'}, status=400)
   #     if not user.check_password(password):
   #         return Response({'message': 'Falsches Passwort'}, status=400)
   #     user_new = authenticate(request, username=user.username, password=password)
   #     protocol = Protocol.objects.create(
   #         user=user_new,
   #         action='LOGIN',
   #         related_object='User'
   #     )

   #     if user_new is None:
   #         protocol.description = 'A User with this email does not exist or wrong password'
   #         protocol.save()
   #         return Response({'message':'A User with this email does not exist or wrong password'}, status=400)
   #     preferred_language = UserSettings.objects.get(customer_user=user).preferred_language#

  #      try:
   #         company = Company.objects.get(owner=user)
   #         if company.blocked:

   #             company_blocked = language_manager.get_text(preferred_language, 'company_blocked')
   #             protocol.description = company_blocked
   #             protocol.save()
   #             return Response({'message': company_blocked}, status=400)
   #     except:
   #         pass#



   #     access_token, refresh_token = create_token_for_user(user)


   #     success_message = language_manager.get_text(preferred_language, 'success_login')
   #     protocol.description = success_message
   #     protocol.save()
   #     return Response({
   #         'message': success_message,
   #         'access_token': str(access_token),
   #         'refresh_token': str(refresh_token),
   #         'permissions': generate_jwt(user_new)
   #     }, status=200)
