from django.urls import path

from company.views import CreateCompanyView, UpdateCompanyView

from company.views import GetCompany

from company.views import InviteUser

from company.views import ChangeRole

from company.views import KickUserFromCompany

from company.views import DeactiveUser

from company.views import DeleteExMembers

from company.views import GetExMembers

from company.views import InvitePartnerToCreate

from company.views import InvitePartnerToPartnerCompany

from company.views import GetPartnerList

from company.views import GetPartnerDetail

urlpatterns = [
    path('create-company/', CreateCompanyView.as_view(), name='create-company'),
    path('update-company/', UpdateCompanyView.as_view(), name='update-company'),
    path('get-company/', GetCompany.as_view(), name='get-company'),
    path('invite-user/', InviteUser.as_view(), name='invite-user'),

    path('change-role/', ChangeRole.as_view(), name='change-role'),
    path('kick-user/', KickUserFromCompany.as_view(), name='kick-user'),
    path('deactivate-user/', DeactiveUser.as_view(), name='deactivate-user'),



    path('invite-partner-to-create/', InvitePartnerToCreate.as_view(), name='invite-partner-to-create'),
    path('invite-partner-to-partnerCompany/', InvitePartnerToPartnerCompany.as_view(), name='invite-partner-to-partnerCompany'),

    path('get-partner-list/', GetPartnerList.as_view(), name='get-partner-list'),
    path('get-partner-detail/', GetPartnerDetail.as_view(), name='get-partner-detail'),

    path('delete-exmembers/', DeleteExMembers.as_view(), name='ex-members'),
    path('get-exmembers/', GetExMembers.as_view(), name='get-exmembers'),
]