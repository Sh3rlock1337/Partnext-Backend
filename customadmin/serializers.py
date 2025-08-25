
from django.contrib.auth.models import User
from rest_framework import serializers

from company.models import Company




class AdminUserSerizalizer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'is_active', 'is_staff', 'is_superuser']

class AdminCompanySerializer(serializers.ModelSerializer):
    owner = AdminUserSerizalizer(many=True, read_only=True)

    class Meta:
        model = Company
        fields = ['id', 'company_name', 'street', 'house_number', 'zip', 'city', 'country', 'phone', 'email', 'created_at', 'updated_at', 'owner', 'staff', 'blocked']
        read_only_fields = ['created_at', 'updated_at', 'owner']

