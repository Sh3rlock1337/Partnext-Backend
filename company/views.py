from django.contrib.auth.models import User
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django_ratelimit.decorators import ratelimit
from rest_framework.views import APIView


# Create your views here.
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.views import APIView
from .models import Company, InvitationCompany, ExMembers, InvitationPartnerToCreate
from .serializers import CompanySerializer, ExMembersSerializer
from usermanager.models import UserSettings
from django.db import models
from simpleapi.views import language_manager

from protocoll.models import Protocol

from utils.checkUserSettings import checkForUser

from partner.models import InvitationPartner

from partner.models import Partner

from partner.serializers import PartnerSerializer


class CreateCompanyView(APIView):
    permission_classes = [IsAuthenticated]

    @method_decorator(ratelimit(key='ip', rate='4/h', method='POST'))
    def post(self, request):
        response = checkForUser(request.user)
        protocol = Protocol.objects.create(
            user=request.user,
            action='CREATE',
            related_object='Company'
        )

        if response == True:

            try:
                usersettings = UserSettings.objects.get(customer_user=request.user)

                if usersettings.is_company_owner:
                    create_company_you_already_have = language_manager.get_text(
                        usersettings.preferred_language, 'create_company_you_already_have')
                    protocol.description = create_company_you_already_have
                    protocol.save()

                    return Response({"message": create_company_you_already_have},
                                    status=status.HTTP_400_BAD_REQUEST)
                print("HIHI")
                if Company.objects.filter(owner=request.user).exists():
                    create_company_you_already_have = language_manager.get_text(
                        usersettings.preferred_language, 'create_company_you_already_have')
                    protocol.description = create_company_you_already_have
                    protocol.save()

                    return Response({"message": create_company_you_already_have}, status=status.HTTP_400_BAD_REQUEST)

                print("HUHU")
                if usersettings.is_invited_user_company:
                    print("HA")
                    company_create_no_permission = language_manager.get_text(
                        usersettings.preferred_language, 'company_create_no_permission')
                    protocol.description = company_create_no_permission
                    protocol.save()

                    return Response({"message": company_create_no_permission}, status=status.HTTP_400_BAD_REQUEST)
                if usersettings.is_invited_user_partner:
                    print("JA")
                    company_create_no_permission = language_manager.get_text(
                        usersettings.preferred_language, 'company_create_no_permission')
                    protocol.description = company_create_no_permission
                    protocol.save()

                    return Response({"message": company_create_no_permission}, status=status.HTTP_400_BAD_REQUEST)
                print("HAHA")
                serializer = CompanySerializer(data=request.data)
                if serializer.is_valid():
                    company_created_successfully = language_manager.get_text(
                        usersettings.preferred_language, 'company_created_successfully')
                    serializer.save(owner=[request.user])
                    #update usersettings to company owner
                    usersettings.is_company_owner = True
                    usersettings.save()
                    protocol.description = company_created_successfully
                    protocol.save()

                    return Response({"message": company_created_successfully, "data": serializer.data},
                                    status=status.HTTP_200_OK)
                else:
                    return Response({"message": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

            except Exception as e:
                return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            protocol.description = response
            protocol.save()

            return Response(response, status=status.HTTP_401_UNAUTHORIZED)

class UpdateCompanyView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        response = checkForUser(request.user)
        protocol = Protocol.objects.create(
            user=request.user,
            action='UPDATE',
            related_object='Company'
        )
        if response == True:
            usersettings = UserSettings.objects.get(customer_user=request.user)

            try:
                # Firma-ID aus den übermittelten Daten abrufen

                # Firma anhand der ID und des Eigentümers abrufen
                company = Company.objects.get(owner=request.user)


                # Prüfen, ob der Benutzer das Recht hat, die Firma zu aktualisieren
                if not usersettings.is_company_owner:
                    company_update_no_permission = language_manager.get_text(usersettings.preferred_language,
                                                                             'company_update_no_permission')
                    protocol.description = company_update_no_permission
                    protocol.save()

                    return Response({"message": company_update_no_permission}, status=status.HTTP_403_FORBIDDEN)
                if company.blocked:

                    company_blocked = language_manager.get_text(usersettings.preferred_language, 'company_blocked')
                    protocol.description = company_blocked
                    protocol.save()

                    return Response({"message": company_blocked}, status=status.HTTP_400_BAD_REQUEST)
                # Daten des Requests mit dem Serializer validieren und aktualisieren
                serializer = CompanySerializer(company, data=request.data,
                                               partial=True)  # partial=True ermöglicht das teilweise Update (PATCH)

                if serializer.is_valid():
                    serializer.save()

                    company_updated_successfully = language_manager.get_text(usersettings.preferred_language,
                                                                             'company_updated_successfully')
                    protocol.description = company_updated_successfully
                    protocol.save()

                    return Response({"message": company_updated_successfully, "data": serializer.data},
                                    status=status.HTTP_200_OK)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            except Company.DoesNotExist:
                company_not_found = language_manager.get_text(usersettings.preferred_language, 'company_not_found')
                protocol.description = company_not_found
                protocol.save()
                return Response({"message": company_not_found}, status=status.HTTP_404_NOT_FOUND)
            except Exception as e:
                print(e)
                return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            protocol.description = response
            protocol.save()
            return Response(response, status=status.HTTP_401_UNAUTHORIZED)
class GetCompany(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        response = checkForUser(request.user)
        if response == True:
            usersettings = UserSettings.objects.get(customer_user=request.user)
            protocol = Protocol.objects.create(
                user=request.user,
                action='GET',
                related_object='Company'
            )

            if usersettings.is_company_owner:
                try:
                    company = Company.objects.get(owner=request.user)
                    serializer = CompanySerializer(company)
                    if company.blocked:
                        company_blocked = language_manager.get_text(usersettings.preferred_language, 'company_blocked')
                        protocol.description = company_blocked
                        protocol.save()
                        return Response({"message": company_blocked}, status=status.HTTP_400_BAD_REQUEST)
                    protocol.description = 'Company found.'
                    protocol.save()

                    return Response(serializer.data, status=status.HTTP_200_OK)
                except Company.DoesNotExist:
                    company_not_found = language_manager.get_text(usersettings.preferred_language, 'company_not_found')
                    protocol.description = company_not_found
                    protocol.save()
                    return Response({"message": company_not_found}, status=status.HTTP_404_NOT_FOUND)
                except Exception as e:
                    return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            else:
                if usersettings.is_invited_user_company:
                    print("invited User")
                    try:
                        company = Company.objects.filter(
                            models.Q(staff=request.user) | models.Q(members=request.user)).first()
                        serializer = CompanySerializer(company)
                        if company.blocked:
                            company_blocked = language_manager.get_text(usersettings.preferred_language,
                                                                        'company_blocked')
                            protocol.description = company_blocked
                            protocol.save()
                            return Response({"message": company_blocked}, status=status.HTTP_400_BAD_REQUEST)
                        protocol.description = 'Company found.'
                        protocol.save()

                        return Response(serializer.data, status=status.HTTP_200_OK)
                    except:
                        company_not_found = language_manager.get_text(usersettings.preferred_language,
                                                                      'company_not_found')
                        protocol.description = company_not_found
                        protocol.save()
                        return Response({"message": company_not_found}, status=status.HTTP_404_NOT_FOUND)
                else:
                    company_not_found = language_manager.get_text(usersettings.preferred_language, 'company_not_found')
                    protocol.description = company_not_found
                    protocol.save()
                    return Response({"message": company_not_found}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response(response, status=status.HTTP_401_UNAUTHORIZED)


class InviteUser(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        response = checkForUser(request.user)
        print(response)
        if response == True:
            usersettings = UserSettings.objects.get(customer_user=request.user)
            preffered_language = usersettings.preferred_language

            if usersettings.is_company_owner:
                try:
                    company = Company.objects.get(owner=request.user)
                    if company.blocked:
                        company_blocked = language_manager.get_text(preffered_language, 'company_blocked')
                        return Response({"message": company_blocked}, status=status.HTTP_400_BAD_REQUEST)
                    else:
                        invite_email = request.data['email']
                        if invite_email == "":
                            company_invite_no_email = language_manager.get_text(preffered_language, 'company_invite_no_email')
                            return Response({"message": company_invite_no_email}, status=status.HTTP_400_BAD_REQUEST)
                        if invite_email == request.user.email:
                            company_invite_no_self = language_manager.get_text(preffered_language, 'company_invite_no_self')
                            return Response({"message": company_invite_no_self}, status=status.HTTP_400_BAD_REQUEST)
                        if InvitationCompany.objects.filter(email=invite_email, company=company).exists():
                            company_invite_already_sent = language_manager.get_text(preffered_language, 'company_invite_already_sent')
                            return Response({"message": company_invite_already_sent}, status=status.HTTP_400_BAD_REQUEST)

                        invitation = InvitationCompany.objects.create(
                            email=invite_email,
                            company=company,
                            invited_by=request.user
                        )




                        invitelink = f"{invitation.token}"
                        print("MAIL SENDEN AN", invite_email)
                        return Response({"message": invitelink}, status=status.HTTP_200_OK)
                except Company.DoesNotExist:
                    return Response({'error': 'Keine Berechtigung für diese Firma'}, status=status.HTTP_403_FORBIDDEN)

            else:
                company_invite_no_permission = language_manager.get_text(preffered_language, 'company_invite_no_permission')

                return Response({"message": company_invite_no_permission}, status=status.HTTP_403_FORBIDDEN)

        else:
            return Response(response, status=status.HTTP_401_UNAUTHORIZED)


class ChangeRole(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        response = checkForUser(request.user)
        print(response)
        if response == True:
            usersettings = UserSettings.objects.get(customer_user=request.user)
            preffered_language = usersettings.preferred_language

            if usersettings.is_company_owner:
                try:
                    company = Company.objects.get(owner=request.user)
                    if company.blocked:
                        company_blocked = language_manager.get_text(preffered_language, 'company_blocked')
                        return Response({"message": company_blocked}, status=status.HTTP_400_BAD_REQUEST)
                    else:
                        try:
                            user_id = request.data['user_id']
                            target_user = User.objects.get(pk=user_id)
                            try:
                                userscompany = Company.objects.filter(
                                    models.Q(staff=target_user) |  models.Q(owner=target_user)).first()

                                if userscompany.blocked:
                                    company_blocked = language_manager.get_text(preffered_language, 'company_blocked')
                                    return Response({"message": company_blocked}, status=status.HTTP_400_BAD_REQUEST)
                                if userscompany == company:

                                    role = request.data['role']

                                    if role == 'staff':
                                        company.staff.add(target_user)
                                        company.owner.remove(target_user)
                                        company_user_role_change_success = language_manager.get_text(preffered_language, 'company_user_role_change_success')
                                        return Response({"message": company_user_role_change_success}, status=status.HTTP_200_OK)


                                    if role == 'owner':
                                        company.staff.remove(target_user)
                                        company.owner.add(target_user)
                                        company_user_role_change_success = language_manager.get_text(preffered_language, 'company_user_role_change_success')
                                        return Response({"message": company_user_role_change_success}, status=status.HTTP_200_OK)

                                else:
                                    users_company_not_found = language_manager.get_text(preffered_language, 'users_company_not_found')
                                    return Response({'message': users_company_not_found}, status=status.HTTP_403_FORBIDDEN)

                            except:
                                users_company_not_found = language_manager.get_text(preffered_language, 'users_company_not_found')
                                return Response({'message': users_company_not_found}, status=status.HTTP_403_FORBIDDEN)
                        except:
                            user_not_found = language_manager.get_text(preffered_language, 'user_not_found')
                            return Response({'message': user_not_found}, status=status.HTTP_403_FORBIDDEN)



                except:
                    company_not_found = language_manager.get_text(preffered_language, 'company_not_found')
                    return Response({'message': company_not_found}, status=status.HTTP_403_FORBIDDEN)
            else:
                company_not_found = language_manager.get_text(preffered_language, 'company_not_found')

                return Response({'message':company_not_found}, status=status.HTTP_403_FORBIDDEN)


class KickUserFromCompany(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        response = checkForUser(request.user)
        print(response)
        if response == True:
            target_user = request.data['user_id']
            usersettings = UserSettings.objects.get(customer_user=request.user)
            try:
                user = User.objects.get(pk=target_user)

                try:
                    user_company = Company.objects.filter(
                        models.Q(staff=target_user)).first()
                    company = Company.objects.get(owner=request.user)
                    if user_company == company:

                        company.staff.remove(user)

                        ExMembers.objects.create(
                            company=company,
                            executed_user=request.user,
                            first_name=user.first_name,
                            last_name=user.last_name,
                        )

                        user.delete()
                        company_user_kicked = language_manager.get_text(usersettings.preferred_language, 'company_user_kicked')
                        return Response({"message": company_user_kicked}, status=status.HTTP_200_OK)
                    else:
                        user_not_found = language_manager.get_text(usersettings.preferred_language, 'user_not_found')
                        return Response({'message': user_not_found}, status=status.HTTP_403_FORBIDDEN)
                except:
                    user_not_found = language_manager.get_text(usersettings.preferred_language, 'user_not_found')
                    return Response({'message': user_not_found}, status=status.HTTP_403_FORBIDDEN)
            except:
                user_not_found = language_manager.get_text(usersettings.preferred_language, 'user_not_found')
                return Response({'message': user_not_found}, status=status.HTTP_403_FORBIDDEN)
        else:
            return Response(response, status=status.HTTP_401_UNAUTHORIZED)

class DeactiveUser(APIView):
    permission_classes =  [IsAuthenticated]

    def post(self, request):
        response = checkForUser(request.user)
        print(response)
        if response == True:
            target_user = request.data['user_id']
            usersettings = UserSettings.objects.get(customer_user=request.user)
            try:
                user = User.objects.get(pk=target_user)

                try:
                    user_company = Company.objects.filter(
                        models.Q(staff=user)).first()
                    company = Company.objects.get(owner=request.user)
                    if user_company == company:
                        if user.is_active:
                            user.is_active = False
                            user.save()
                            company_user_deactivated = language_manager.get_text(usersettings.preferred_language, 'company_user_deactivated')
                            return Response({"message": company_user_deactivated}, status=status.HTTP_200_OK)
                        else:
                            user.is_active = True
                            user.save()
                            company_user_activated = language_manager.get_text(usersettings.preferred_language, 'company_user_activated')
                            return Response({"message": company_user_activated}, status=status.HTTP_200_OK)

                    else:
                        user_not_found = language_manager.get_text(usersettings.preferred_language, 'user_not_found')
                        return Response({'message': user_not_found}, status=status.HTTP_403_FORBIDDEN)
                except:
                    user_not_found = language_manager.get_text(usersettings.preferred_language, 'user_not_found')
                    return Response({'message': user_not_found}, status=status.HTTP_403_FORBIDDEN)
            except:
                user_not_found = language_manager.get_text(usersettings.preferred_language, 'user_not_found')
                return Response({'message': user_not_found}, status=status.HTTP_403_FORBIDDEN)
        else:
            return Response(response, status=status.HTTP_401_UNAUTHORIZED)


class DeleteExMembers(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        response = checkForUser(request.user)
        print(response)
        if response == True:
            usersettings = UserSettings.objects.get(customer_user=request.user)
            if usersettings.is_company_owner:
                try:
                    company = Company.objects.get(owner=request.user)
                    if company.blocked:
                        company_blocked = language_manager.get_text(usersettings.preferred_language, 'company_blocked')
                        return Response({"message": company_blocked}, status=status.HTTP_400_BAD_REQUEST)
                    else:
                        id = request.data['id']

                        try:
                            #ich will nur die id in exmembers löschen
                            exmembers = ExMembers.objects.get(id=id, company=company)
                            exmembers.delete()
                            company_exmembers_deleted = language_manager.get_text(usersettings.preferred_language,
                                                                                  'company_exmembers_deleted')
                            return Response({"message": company_exmembers_deleted}, status=status.HTTP_200_OK)
                        except:
                            company_exmembers_not_found = language_manager.get_text(usersettings.preferred_language, 'company_exmembers_not_found')
                            return Response({'message': company_exmembers_not_found}, status=status.HTTP_403_FORBIDDEN)


                except:
                    company_not_found = language_manager.get_text(usersettings.preferred_language, 'company_not_found')
                    return Response({'message': company_not_found}, status=status.HTTP_403_FORBIDDEN)
            else:
                company_update_no_permission = language_manager.get_text(usersettings.preferred_language, 'company_update_no_permission')

                return Response({'message': company_update_no_permission}, status=status.HTTP_403_FORBIDDEN)
        else:
            return Response(response, status=status.HTTP_401_UNAUTHORIZED)

class GetExMembers(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        response = checkForUser(request.user)
        print(response)
        if response == True:
            usersettings = UserSettings.objects.get(customer_user=request.user)
            if usersettings.is_company_owner:
                try:
                    print(request.user)

                    company = Company.objects.get(owner=request.user)
                    print(company)
                    if company.blocked:
                        company_blocked = language_manager.get_text(usersettings.preferred_language, 'company_blocked')
                        return Response({"message": company_blocked}, status=status.HTTP_400_BAD_REQUEST)
                    else:
                        exmembers = ExMembers.objects.filter(company=company)
                        serializer = ExMembersSerializer(exmembers, many=True)
                        return Response(serializer.data, status=status.HTTP_200_OK)
                except:
                    company_not_found = language_manager.get_text(usersettings.preferred_language, 'company_not_found')
                    return Response({'message': company_not_found}, status=status.HTTP_403_FORBIDDEN)
            else:
                company_update_no_permission = language_manager.get_text(usersettings.preferred_language, 'company_update_no_permission')

                return Response({'message': company_update_no_permission}, status=status.HTTP_403_FORBIDDEN)
        else:
            return Response(response, status=status.HTTP_401_UNAUTHORIZED)

class InvitePartnerToCreate(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        response = checkForUser(request.user)
        print(response)
        if response == True:
            usersettings = UserSettings.objects.get(customer_user=request.user)
            company = Company.objects.get(models.Q(owner=request.user) | models.Q(staff=request.user))
            if company.blocked:
                company_blocked = language_manager.get_text(usersettings.preferred_language, 'company_blocked')
                return Response({"message": company_blocked}, status=status.HTTP_400_BAD_REQUEST)
            if InvitationPartnerToCreate.objects.filter(email=request.data['email'], company=company).exists():
                company_invite_already_sent = language_manager.get_text(usersettings.preferred_language, 'company_invite_already_sent')
                return Response({"message": company_invite_already_sent}, status=status.HTTP_400_BAD_REQUEST)


            invitationforpartner = InvitationPartnerToCreate.objects.create(
                email=request.data['email'],
                invited_by=request.user,
                company=company
            )
            invitationforpartner.save()
            print("MAIL SENDEN AN", request.data['email'])
            return Response({"message": "Invitation sent"}, status=status.HTTP_200_OK)
        else:
            print("NEIN")
            return Response(response, status=status.HTTP_401_UNAUTHORIZED)


class InvitePartnerToPartnerCompany(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        response = checkForUser(request.user)
        print(response)
        print(request.user)
        if response == True:
            usersettings = UserSettings.objects.get(customer_user=request.user)
            try:
                company = Company.objects.get(models.Q(owner=request.user) | models.Q(staff=request.user))
                print(company)
                if company.blocked:
                    company_blocked = language_manager.get_text(usersettings.preferred_language, 'company_blocked')
                    return Response({"message": company_blocked}, status=status.HTTP_400_BAD_REQUEST)
                print("not blocked")
                try:
                    if InvitationPartner.objects.filter(email=request.data['email'], company=company).exists():
                        company_invite_already_sent = language_manager.get_text(usersettings.preferred_language, 'company_invite_already_sent')
                        return Response({"message": company_invite_already_sent}, status=status.HTTP_400_BAD_REQUEST)
                except:
                    print("no invite")
                    pass

                print("du bist es")
                partnerid = request.data['partnerid']
                print(partnerid)
                try:
                    find_partner = Partner.objects.get(pk=partnerid)
                    print(find_partner)
                    if find_partner.partner_company == company:
                        InvitationPartner.objects.create(
                            email=request.data['email'],
                            invited_by=request.user,
                            partner=find_partner
                        )
                        return Response({"message": "Invitation sent"}, status=status.HTTP_200_OK)
                    else:
                        print("andere partner")
                        partner_not_found = language_manager.get_text(usersettings.preferred_language, 'partner_not_found')
                        return Response({'message': partner_not_found}, status=status.HTTP_403_FORBIDDEN)
                except:
                    print("not found partner")
                    partner_not_found = language_manager.get_text(usersettings.preferred_language, 'partner_not_found')
                    return Response({'message': partner_not_found}, status=status.HTTP_403_FORBIDDEN)

            except:
                company_not_found = language_manager.get_text(usersettings.preferred_language, 'company_not_found')
                return Response({'message': company_not_found}, status=status.HTTP_403_FORBIDDEN)
        else:
            return Response(response, status=status.HTTP_401_UNAUTHORIZED)


class GetPartnerList(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        response = checkForUser(request.user)
        print(response)
        if response == True:
            try:
                usersettings = UserSettings.objects.get(customer_user=request.user)
                company = Company.objects.get(models.Q(owner=request.user) | models.Q(staff=request.user))

                if company.blocked:
                    company_blocked = language_manager.get_text(usersettings.preferred_language, 'company_blocked')
                    return Response({"message": company_blocked}, status=status.HTTP_400_BAD_REQUEST)

                partners = Partner.objects.filter(partner_company=company)


                # Überprüfen, ob es gesperrte Partner gibt

                serializer = PartnerSerializer(partners, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except UserSettings.DoesNotExist:
                return Response({"message": "User settings not found."}, status=status.HTTP_404_NOT_FOUND)
            except Company.DoesNotExist:
                return Response({"message": "Company not found."}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response(response, status=status.HTTP_401_UNAUTHORIZED)

class GetPartnerDetail(APIView):
    pass