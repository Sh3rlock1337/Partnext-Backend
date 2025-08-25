"""
URL configuration for partnextbackend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.urls import path, include
from django.contrib.auth.models import User, Group
from django.contrib import admin

admin.autodiscover()
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from rest_framework import generics, permissions, serializers

from oauth2_provider import urls as oauth2_urls
from oauth2_provider.contrib.rest_framework import TokenHasReadWriteScope, TokenHasScope
import requests
from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken




urlpatterns = [
    path('admin/', admin.site.urls),
    path('o/', include(oauth2_urls)),

  #  path('auth/', include('allauth.urls')),

    path('simple-api/', include('simpleapi.urls')),
    path('usermanager/', include('usermanager.urls')),
    path('company/', include('company.urls')),
    path('permissions/', include('permissions.urls')),
    path("customadmin/", include("customadmin.urls")),
    path('partner/', include('partner.urls')),
]


