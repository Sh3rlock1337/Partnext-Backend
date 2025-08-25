from django.contrib.auth.models import User
from rest_framework import serializers
from company.models import Company

from company.models import ExMembers

class CompanyUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'is_active', 'is_staff', 'is_superuser']

class CompanySerializer(serializers.ModelSerializer):
    owner = CompanyUserSerializer(many=True, read_only=True)
    staff = CompanyUserSerializer(many=True, read_only=True)  # Optional: Falls du auch `staff` als verschachtelte Objekte ausgeben möchtest

    class Meta:
        model = Company
        fields = ['id', 'company_name', 'street', 'house_number', 'zip', 'city', 'country', 'phone', 'email', 'created_at', 'updated_at', 'owner', 'staff', 'blocked']
        read_only_fields = ['created_at', 'updated_at', 'owner']




class ExMembersSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExMembers
        fields = ['id', 'company', 'first_name', 'last_name', 'created_at', 'executed_user']
        read_only_fields = ['created_at']
