from django.urls import path

from partner.views import CreatePartner, DeleteLeadStatus, ChangeLeadStatus, GetLead, GetLeadList, CreateLead, DeleteExMembers, GetExMembers, KickPartnerFromCompany, UpdatePartner, GetPartner

from partner.views import EditLead

from partner.views import EditContact, GetContact, CreateContact, DeleteContact

urlpatterns = [
    path('create-partner/', CreatePartner.as_view(), name='create-company'),
    path('update-partner/', UpdatePartner.as_view(), name='update-company'),
    path('get-partner/', GetPartner.as_view(), name='get-company'),

    path('kick-partner/', KickPartnerFromCompany.as_view(), name='kick-partner'),
    path('get-exmembers/', GetExMembers.as_view(), name='get-exmembers'),

    path('delete-exmembers/', DeleteExMembers.as_view(), name='ex-members'),

    path('create-contact/', CreateContact.as_view(), name='create-contact'),
    path('get-contact/', GetContact.as_view(), name='get-contact'),
    path('delete-contact/', DeleteContact.as_view(), name='delete-contact'),
    path('edit-contact/', EditContact.as_view(), name='edit-contact'),


    path('create-lead/', CreateLead.as_view(), name='create-lead'),
    path('get-lead-list/', GetLeadList.as_view(), name='get-lead'),
    path('change-status/', ChangeLeadStatus.as_view(), name='change-status'),
    path('delete-lead/', DeleteLeadStatus.as_view(), name='delete-members'),
    path('get-lead/', GetLead.as_view(), name='get-lead'),
    path('edit-lead/', EditLead.as_view(), name='edit-lead'),
]