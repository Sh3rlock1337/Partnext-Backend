from django.contrib.auth.models import User
from rest_framework.permissions import IsAdminUser
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response

from company.serializers import CompanySerializer
from protocoll.models import Protocol
from simpleapi.views import language_manager
from usermanager.models import UserSettings

from company.models import Company

from simpleapi.serializers import UserSerializer

from utils.checkUserSettings import checkForUser

from company.models import CompanyRelationship

from customadmin.serializers import AdminCompanySerializer


# Create your views here.
class CreatCompany(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request):
        if request.user.is_authenticated:
            protocol = Protocol.objects.create(
                user=request.user,
                action='CREATE',
                related_object='Company'
            )
            try:


                try:
                    id = request.data['owner']
                    print(id)
                    print(2)
                    userid = User.objects.get(pk=id)
                    print(3)
                    usersettings = UserSettings.objects.get(customer_user=userid)
                    if usersettings.email_verified:
                        if usersettings.is_company_owner:
                            create_company_you_already_have = language_manager.get_text(
                                usersettings.preferred_language, 'create_company_you_already_have')
                            protocol.description = create_company_you_already_have
                            protocol.save()

                            return Response({"message": create_company_you_already_have},
                                            status=status.HTTP_400_BAD_REQUEST)

                        if Company.objects.filter(owner=userid).exists():
                            create_company_you_already_have = language_manager.get_text(
                                usersettings.preferred_language, 'create_company_you_already_have')
                            protocol.description = create_company_you_already_have
                            protocol.save()

                            return Response({"message": create_company_you_already_have},
                                            status=status.HTTP_400_BAD_REQUEST)

                        if usersettings.is_invited_user_company:
                            company_create_no_permission = language_manager.get_text(
                                usersettings.preferred_language, 'company_create_no_permission')
                            protocol.description = company_create_no_permission
                            protocol.save()

                            return Response({"message": company_create_no_permission}, status=status.HTTP_400_BAD_REQUEST)
                        if usersettings.is_invited_user_partner:
                            company_create_no_permission = language_manager.get_text(
                                usersettings.preferred_language, 'company_create_no_permission')
                            protocol.description = company_create_no_permission
                            protocol.save()

                            return Response({"message": company_create_no_permission}, status=status.HTTP_400_BAD_REQUEST)
                        serializer = CompanySerializer(data=request.data)
                        if serializer.is_valid():
                            company_created_successfully = language_manager.get_text(
                                usersettings.preferred_language, 'company_created_successfully')
                            serializer.save(owner=userid)
                            # update usersettings to company owner
                            usersettings.is_company_owner = True
                            usersettings.save()
                            protocol.description = company_created_successfully
                            protocol.save()

                            return Response({"message": company_created_successfully, "data": serializer.data},
                                            status=status.HTTP_200_OK)
                        else:
                            return Response({"message": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
                    else:
                        email_not_verified = language_manager.get_text(usersettings.preferred_language,
                                                                       'email_not_verified')
                        protocol.description = email_not_verified

                        protocol.save()
                        return Response({"message": email_not_verified}, status=status.HTTP_400_BAD_REQUEST)
                except:
                    print(request.data)
                    serializer = CompanySerializer(data=request.data)
                    if serializer.is_valid():
                        company_created_successfully = language_manager.get_text(
                            'de', 'company_created_successfully')
                        Company.objects.create(
                            company_name=request.data['company_name'],
                            street=request.data['street'],
                            house_number=request.data['house_number'],
                            city=request.data['city'],
                            country=request.data['country'],
                            phone=request.data['phone'],
                            email=request.data['email'],

                        )
                        # update usersettings to company owner
                        protocol.description = company_created_successfully
                        protocol.save()

                        return Response({"message": company_created_successfully, "data": serializer.data},
                                        status=status.HTTP_200_OK)
                    else:
                        return Response({"message": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

class BlockCompany(APIView):
    #permission nur als admin
    permission_classes = [IsAdminUser]

    def post(self, request):
        if request.user.is_staff:
            usersettings = UserSettings.objects.get(customer_user=request.user)
            protocol = Protocol.objects.create(
                user=request.user,
                action='UPDATE',
                related_object='Company'
            )
            try:

                company = Company.objects.get(id=request.data['id'])
                if company.blocked:
                    company.blocked = False
                    company_admin_unblocked = language_manager.get_text(usersettings.preferred_language, 'company_admin_unblocked')
                    protocol.description = company_admin_unblocked + ' ' + company.company_name
                    protocol.save()
                    company.save()
                    return Response({"message": company_admin_unblocked}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    company.blocked = True
                    company.save()
                    company_admin_blocked = language_manager.get_text(usersettings.preferred_language, 'company_admin_blocked')
                    protocol.description = company_admin_blocked + ' ' + company.company_name
                    protocol.save()
                    company.save()
                    return Response({"message": company_admin_blocked}, status=status.HTTP_200_OK)


            except:
                company_not_found = language_manager.get_text(usersettings.preferred_language, 'company_not_found')
                protocol.description = company_not_found + ': ' + str(request.data['id'])
                protocol.save()

                return Response({"message": company_not_found}, status=status.HTTP_404_NOT_FOUND)


        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

class GetCompanyList(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        if request.user.is_staff:
            usersettings = UserSettings.objects.get(customer_user=request.user)
            protocol = Protocol.objects.create(
                user=request.user,
                action='GET',
                related_object='Company'
            )
            try:
                companies = Company.objects.all()
                serializer = AdminCompanySerializer(companies, many=True)
                protocol.description = 'Company list fetched.'
                protocol.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)


class GetCompanyByID(APIView):
    permission_classes = [IsAdminUser]

    def post(self,request):
        if request.user.is_staff:
            usersettings = UserSettings.objects.get(customer_user=request.user)
            protocol = Protocol.objects.create(
                user=request.user,
                action='GET',
                related_object='Company'
            )
            try:
                company = Company.objects.get(id=request.data['id'])
                serializer = CompanySerializer(company)
                protocol.description = 'Company with id ' + str(request.data['id']) + ' fetched.'
                protocol.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            except:
                company_not_found = language_manager.get_text(usersettings.preferred_language, 'company_not_found')
                protocol.description = company_not_found + ': ' + str(request.data['id'])
                protocol.save()
                return Response({"message": company_not_found}, status=status.HTTP_404_NOT_FOUND)



class GetUserList(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        if request.user.is_staff:
            all_users = User.objects.all()
            serializer = UserSerializer(all_users, many=True)  # Serialisiere die Benutzerliste
            return Response({"users": serializer.data}, status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)




class BlockUser(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request):
        if request.user.is_staff:
            id = request.data['id']
            try:
                user = User.objects.get(pk=id)
            except:
                return Response({"message":"User not found" }, status=status.HTTP_404_NOT_FOUND)
            if user.is_active:
                user.is_active = False
                user.save()
                return Response(status=status.HTTP_200_OK)
            else:
                user.is_active = True
                user.save()
                return Response(status=status.HTTP_200_OK)

        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)


class AddCompanyToCompany(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request):
        response = checkForUser(request.user)
        if response == True:
            print("TRUE")
            usersettings = UserSettings.objects.get(customer_user=request.user)
            preferred_language = usersettings.preferred_language
            company_id = None
            company_sub_id = None
            try:
                company_id = request.data['company_id']
                company_sub_id = request.data['company_sub_id']
            except:
                company_not_found = language_manager.get_text(preferred_language, 'company_not_found')
                return Response({"message": company_not_found}, status=status.HTTP_404_NOT_FOUND)

            try:
                company = Company.objects.get(id=company_id)
                sub_company = Company.objects.get(id=company_sub_id)
                print(company)
                print(sub_company)
                if company == sub_company:

                    return Response({"message": "You can't add a company to itself"}, status=status.HTTP_400_BAD_REQUEST)

                if company.blocked:
                    company_blocked = language_manager.get_text(preferred_language, 'company_blocked')
                    return Response({"message": company_blocked}, status=status.HTTP_400_BAD_REQUEST)
                if sub_company.blocked:
                    company_blocked = language_manager.get_text(preferred_language, 'company_blocked')
                    return Response({"message": company_blocked}, status=status.HTTP_400_BAD_REQUEST)

                if CompanyRelationship.objects.filter(from_company=company, to_company=sub_company).exists():
                    company_already_added = language_manager.get_text(preferred_language, 'company_already_added')
                    return Response({"message": company_already_added}, status=status.HTTP_400_BAD_REQUEST)
                if CompanyRelationship.objects.filter(from_company=sub_company, to_company=company).exists():
                    company_already_added = language_manager.get_text(preferred_language, 'company_already_added')
                    return Response({"message": company_already_added}, status=status.HTTP_400_BAD_REQUEST)

                CompanyRelationship.objects.create(from_company=company, to_company=sub_company)


                return Response({"message": "Company added to company"}, status=status.HTTP_200_OK)

            except:
                company_not_found = language_manager.get_text(preferred_language, 'company_not_found')
                return Response({"message": company_not_found}, status=status.HTTP_404_NOT_FOUND)



        else:
            return Response(response, status=status.HTTP_401_UNAUTHORIZED)


class RemoveCompanyFromCompany(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request):
        response = checkForUser(request.user)
        if response == True:
            print("JA")
            usersettings = UserSettings.objects.get(customer_user=request.user)
            perffered_language = usersettings.preferred_language

            company_id = None
            company_sub_id = None
            try:
                company_id = request.data['company_id']
                company_sub_id = request.data['company_sub_id']
            except:
                company_not_found = language_manager.get_text(perffered_language, 'company_not_found')
                return Response({"message": company_not_found}, status=status.HTTP_404_NOT_FOUND)

            try:
                company = Company.objects.get(id=company_id)
                sub_company = Company.objects.get(id=company_sub_id)

                if company == sub_company:
                    return Response({"message": "You can't remove a company from itself"}, status=status.HTTP_400_BAD_REQUEST)

                if company.blocked:
                    company_blocked = language_manager.get_text(perffered_language, 'company_blocked')
                    return Response({"message": company_blocked}, status=status.HTTP_400_BAD_REQUEST)
                if sub_company.blocked:
                    company_blocked = language_manager.get_text(perffered_language, 'company_blocked')
                    return Response({"message": company_blocked}, status=status.HTTP_400_BAD_REQUEST)

                if CompanyRelationship.objects.filter(from_company=company, to_company=sub_company).exists():

                    CompanyRelationship.objects.filter(from_company=company, to_company=sub_company).delete()

                    return Response({"message": "Company removed from company"}, status=status.HTTP_200_OK)
                else:
                    company_not_added = language_manager.get_text(perffered_language, 'company_not_added')
                    return Response({"message": company_not_added}, status=status.HTTP_400_BAD_REQUEST)
            except:
                company_not_found = language_manager.get_text(perffered_language, 'company_not_found')
                return Response({"message": company_not_found}, status=status.HTTP_404_NOT_FOUND)







        else:
            return Response(response, status=status.HTTP_401_UNAUTHORIZED)