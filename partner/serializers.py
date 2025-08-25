from partner.models import Partner
from rest_framework import serializers

from partner.models import ExMembers

from partner.models import Lead

from partner.models import Contact


class PartnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Partner
        fields = ['id', 'partner_name', 'partner_street', 'partner_house_number', 'partner_zip', 'partner_city', 'partner_country', 'partner_phone', 'partner_email', 'partner_created_at', 'partner_updated_at', 'partner_owner', "partner_company", "partner_blocked"]
        read_only_fields = ['created_at', 'updated_at', 'partner_owner', "partner_company"]

class ExMembersSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExMembers
        fields = ['id', 'partner', 'first_name', 'last_name', 'created_at', 'executed_user']
        read_only_fields = ['created_at']

class LeadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lead
        fields = ['id', 'first_name', 'last_name', 'email', 'phone', 'company', 'street', 'house_number', 'city', 'country', 'zip', 'created_at', 'updated_at', 'blocked', 'partner', 'creator', 'lead_uuid', 'lead_note', 'lead_status']
        read_only_fields = ['created_at', 'updated_at', 'creator', 'lead_uuid']

class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = [
            'id',
            'contact_uuid',
            'contact_first_name',
            'contact_last_name',
            'contact_email',
            'contact_adress',
            'contact_phonenumber',
            'contact_note',
            'contact_created_at',
            'contact_updated_at',
            'connected_lead',
            'contact_status',
            'contact_creator',
            'contact_position'
        ]
        read_only_fields = ['contact_created_at', 'contact_updated_at', 'contact_uuid']