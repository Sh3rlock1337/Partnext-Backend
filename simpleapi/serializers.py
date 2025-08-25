from rest_framework import serializers
from django.urls import path, include
from django.contrib.auth.models import User, Group
from django.contrib import admin
admin.autodiscover()

from rest_framework import generics, permissions, serializers

from oauth2_provider import urls as oauth2_urls
from oauth2_provider.contrib.rest_framework import TokenHasReadWriteScope, TokenHasScope

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email', "first_name", "last_name", "is_active")

