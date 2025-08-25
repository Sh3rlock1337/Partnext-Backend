from django.contrib.auth.models import User
from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from utils.checkUserSettings import checkForUser
from rest_framework.response import Response
from rest_framework import status

from usermanager.models import UserSettings

from partner.models import Partner
from django.db import models
from partner.serializers import PartnerSerializer

from company.models import InvitationPartnerToCreate

from partner.models import ExMembers

from partner.serializers import ExMembersSerializer

from partner.serializers import LeadSerializer


# Create your views here.
class CreatePartner(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        response = checkForUser(request.user)
        print(response)
        if response == True:
            print("jJJ")

            usersettings = UserSettings.objects.get(customer_user=request.user)
            if usersettings.is_invited_user_partner:
                try:
                    print("j??a")
                    partner = Partner.objects.get(
                        models.Q(partner_owner=request.user) | models.Q(partner_staff=request.user))
                    return Response({"message": "You already have a partnercompany"},
                                    status=status.HTTP_400_BAD_REQUEST)
                except Partner.DoesNotExist:
                    pass
                # return Response("You are already a partner", status=status.HTTP_400_BAD_REQUEST)

                if usersettings.is_invited_user_company:
                    return Response({"message": "You are already in a company"}, status=status.HTTP_400_BAD_REQUEST)
                if usersettings.is_company_owner:
                    return Response({"message": "You are already a company owner"}, status=status.HTTP_400_BAD_REQUEST)

                serializer = PartnerSerializer(data=request.data)
                print(serializer)
                print("1")
                # füg serializer partner_owner=[request.user] hinzu
                try:
                    invite = InvitationPartnerToCreate.objects.get(partner_to_create_used_by=request.user)
                    print(invite.company)
                    if serializer.is_valid():
                        serializer.save(partner_owner=[request.user], partner_company=invite.company)

                        # update usersettings to company owner
                        usersettings.save()
                        return Response(serializer.data, status=status.HTTP_201_CREATED)
                    else:
                        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                except:
                    return Response({"message": "You are not invited to create a partner"},
                                    status=status.HTTP_400_BAD_REQUEST)
            else:

                return Response({"message": "You are not a partner"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(response, status=status.HTTP_401_UNAUTHORIZED)


class UpdatePartner(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        response = checkForUser(request.user)
        if response == True:
            print("ja")
            usersettings = UserSettings.objects.get(customer_user=request.user)
            if usersettings.is_invited_user_company:
                return Response({"message": "You are already in a company"}, status=status.HTTP_400_BAD_REQUEST)
            if usersettings.is_company_owner:
                return Response({"message": "You are already a company owner"}, status=status.HTTP_400_BAD_REQUEST)

            if usersettings.is_invited_user_partner:
                try:
                    # print all partner
                    partner = Partner.objects.get(partner_owner=request.user)
                    # mit dem partner serializer den partner updaten
                    serializer = PartnerSerializer(partner, data=request.data)
                    if serializer.is_valid():
                        serializer.save()
                        return Response(serializer.data, status=status.HTTP_200_OK)
                    else:
                        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

                except:
                    print("hihi")
                    return Response({"message": "You are not a partner"}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({"message": "You are not a partner"}, status=status.HTTP_400_BAD_REQUEST)




        else:
            return Response(response, status=status.HTTP_401_UNAUTHORIZED)


class GetPartner(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        response = checkForUser(request.user)
        if response == True:
            try:
                partner = Partner.objects.get(
                    models.Q(partner_owner=request.user) | models.Q(partner_staff=request.user))
                serializer = PartnerSerializer(partner)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except:
                return Response({"message": "You are not a partner"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(response, status=status.HTTP_401_UNAUTHORIZED)


class KickPartnerFromCompany(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        response = checkForUser(request.user)
        if response == True:
            usersettings = UserSettings.objects.get(customer_user=request.user)
            if usersettings.is_invited_user_partner:
                own_partner = Partner.objects.get(partner_owner=request.user)
                if own_partner:
                    try:
                        try:
                            email = request.data['email']
                            if email == "":
                                return Response({"message": "Email not provided"}, status=status.HTTP_400_BAD_REQUEST)
                        except:
                            return Response({"message": "Email not provided"}, status=status.HTTP_400_BAD_REQUEST)

                        user_to_kick = User.objects.get(email=email)
                        partner = Partner.objects.get(
                            models.Q(partner_owner=user_to_kick) | models.Q(partner_staff=user_to_kick)
                        )

                        if partner == own_partner:
                            partner.partner_staff.remove(user_to_kick)
                            partner.partner_owner.remove(user_to_kick)

                            ExMembers.objects.create(
                                partner=partner,
                                first_name=user_to_kick.first_name,
                                last_name=user_to_kick.last_name,
                                executed_user=request.user

                            )
                            user_to_kick.delete()

                            return Response({"message": "Partner was kicked"}, status=status.HTTP_200_OK)
                        else:
                            return Response({"message": "This is not your partner"}, status=status.HTTP_400_BAD_REQUEST)
                    except Partner.DoesNotExist:
                        return Response({"message": "Partner does not exist"}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response({"message": "You are not a partner owner"}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({"message": "You are not a company owner"}, status=status.HTTP_400_BAD_REQUEST)


class GetExMembers(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        response = checkForUser(request.user)
        if response == True:
            try:
                partner = Partner.objects.get(partner_owner=request.user)
                ex_members = ExMembers.objects.filter(partner=partner)

                if not ex_members.exists():
                    return Response({"message": "No ex-members found for this partner"},
                                    status=status.HTTP_404_NOT_FOUND)

                serializer = ExMembersSerializer(ex_members, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except Partner.DoesNotExist:
                return Response({"message": "You are not a partner"}, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(response, status=status.HTTP_401_UNAUTHORIZED)


class DeleteExMembers(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        response = checkForUser(request.user)
        if response == True:
            print("ja")
            usersettings = UserSettings.objects.get(customer_user=request.user)
            if usersettings.is_invited_user_partner:
                own_partner = Partner.objects.get(partner_owner=request.user)
                if own_partner:
                    try:
                        id = request.data['id']
                        if id == "":
                            return Response({"message": "Id not provided"}, status=status.HTTP_400_BAD_REQUEST)
                        try:
                            exmembers = ExMembers.objects.get(id=id)
                            if exmembers.partner == own_partner:
                                exmembers.delete()
                                return Response({"message": "Ex member was deleted"}, status=status.HTTP_200_OK)
                            else:
                                return Response({"message": "This is not your partner"},
                                                status=status.HTTP_400_BAD_REQUEST)
                        except ExMembers.DoesNotExist:
                            return Response({"message": "Ex member does not exist"}, status=status.HTTP_400_BAD_REQUEST)

                    except Partner.DoesNotExist:
                        return Response({"message": "Ex member does not exist"}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response({"message": "You are not a partner owner"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(response, status=status.HTTP_401_UNAUTHORIZED)


class CreateLead(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        response = checkForUser(request.user)
        if response == True:
            try:
                partner = Partner.objects.get(
                    models.Q(partner_owner=request.user) | models.Q(partner_staff=request.user))
                serializer = LeadSerializer(data=request.data)
                if serializer.is_valid():
                    serializer.save(partner=partner, creator=[request.user])
                    return Response(serializer.data, status=status.HTTP_201_CREATED)
                else:
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            except Partner.DoesNotExist:
                return Response({"message": "You are not a partner"}, status=status.HTTP_400_BAD_REQUEST)


class GetLeadList(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        response = checkForUser(request.user)
        if response == True:
            try:
                partner = Partner.objects.get(
                    models.Q(partner_owner=request.user) | models.Q(partner_staff=request.user))
                leads = partner.leads.all()
                serializer = LeadSerializer(leads, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except Partner.DoesNotExist:
                return Response({"message": "You are not a partner"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(response, status=status.HTTP_401_UNAUTHORIZED)


class GetLead(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        response = checkForUser(request.user)
        if response == True:
            try:
                partner = Partner.objects.get(
                    models.Q(partner_owner=request.user) | models.Q(partner_staff=request.user))
                try:
                    id = request.data['id']
                    if id == "":
                        return Response({"message": "Id not provided"}, status=status.HTTP_400_BAD_REQUEST)
                except:
                    return Response({"message": "Id not provided"}, status=status.HTTP_400_BAD_REQUEST)

                lead = partner.leads.get(id=id)
                serializer = LeadSerializer(lead)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except Partner.DoesNotExist:
                return Response({"message": "You are not a partner"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(response, status=status.HTTP_401_UNAUTHORIZED)


class ChangeLeadStatus(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        response = checkForUser(request.user)
        if response == True:
            try:
                partner = Partner.objects.get(
                    models.Q(partner_owner=request.user) | models.Q(partner_staff=request.user))
                try:
                    id = request.data['id']
                    if id == "":
                        return Response({"message": "Id not provided"}, status=status.HTTP_400_BAD_REQUEST)
                except:
                    return Response({"message": "Id not provided"}, status=status.HTTP_400_BAD_REQUEST)
                try:
                    bodystatus = request.data['status']
                    if bodystatus == "":
                        return Response({"message": "Status not provided"}, status=status.HTTP_400_BAD_REQUEST)
                except:
                    return Response({"message": "Status not provided"}, status=status.HTTP_400_BAD_REQUEST)
                print(id)
                print(bodystatus)
                lead = partner.leads.get(id=id)
                lead.lead_status = bodystatus
                lead.save()
                return Response({"message": "Lead status was changed"}, status=status.HTTP_200_OK)
            except Partner.DoesNotExist:
                return Response({"message": "You are not a partner"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(response, status=status.HTTP_401_UNAUTHORIZED)

class DeleteLeadStatus(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        response = checkForUser(request.user)
        if response == True:
            try:
                partner = Partner.objects.get(
                    models.Q(partner_owner=request.user))
                try:
                    id = request.data['id']
                    if id == "":
                        return Response({"message": "Id not provided"}, status=status.HTTP_400_BAD_REQUEST)
                except:
                    return Response({"message": "Id not provided"}, status=status.HTTP_400_BAD_REQUEST)
                lead = partner.leads.get(id=id)
                lead.delete()
                return Response({"message": "Lead was deleted"}, status=status.HTTP_200_OK)
            except Partner.DoesNotExist:
                return Response({"message": "You are not a partner"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(response, status=status.HTTP_401_UNAUTHORIZED)

class EditLead(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        response = checkForUser(request.user)
        if response == True:
            try:
                partner = Partner.objects.get(
                    models.Q(partner_owner=request.user) | models.Q(partner_staff=request.user))
                try:
                    id = request.data['id']
                    if id == "":
                        return Response({"message": "Id not provided"}, status=status.HTTP_400_BAD_REQUEST)
                except:
                    return Response({"message": "Id not provided"}, status=status.HTTP_400_BAD_REQUEST)
                lead = partner.leads.get(id=id)
                serializer = LeadSerializer(lead, data=request.data)
                if serializer.is_valid():
                    serializer.save()
                    return Response(serializer.data, status=status.HTTP_200_OK)
                else:
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            except Partner.DoesNotExist:
                return Response({"message": "You are not a partner"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(response, status=status.HTTP_401_UNAUTHORIZED)


class EditContact(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        response = checkForUser(request.user)
        if response == True:
            pass


class DeleteContact(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        response = checkForUser(request.user)
        if response == True:
            pass
class GetContact(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        response = checkForUser(request.user)
        if response == True:
            pass

class CreateContact(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        response = checkForUser(request.user)
        if response == True:
            pass
