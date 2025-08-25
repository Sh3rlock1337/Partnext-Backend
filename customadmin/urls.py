from django.urls import path



from customadmin.views import GetUserList, BlockUser, CreatCompany, GetCompanyList, BlockCompany

from customadmin.views import AddCompanyToCompany

from customadmin.views import RemoveCompanyFromCompany

from customadmin.views import GetCompanyByID

urlpatterns = [
    path("create-company/", CreatCompany.as_view(), name="create-company"),
    path('block-company/', BlockCompany.as_view(), name='block-company'),

    path('get-companylist/', GetCompanyList.as_view(), name='admin-get-companylist'),
    path('get-company-by-id/', GetCompanyByID.as_view(), name='admin-get-company-by-id'),

    path('get-userlist/', GetUserList.as_view(), name='admin-get-userlist'),
    path('block-user/', BlockUser.as_view(), name='block-user'),

    path('add-company-to-company/', AddCompanyToCompany.as_view(), name='add-company-to-company'),
    path('remove-company-from-company/', RemoveCompanyFromCompany.as_view(), name='remove-company-from-company'),
]