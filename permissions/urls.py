from django.urls import path


from permissions.views import GroupList, PermissionList


urlpatterns = [

    path('groups/', GroupList.as_view(), name='group-list'),
    path('permissions/', PermissionList.as_view(), name='permission-list'),

]