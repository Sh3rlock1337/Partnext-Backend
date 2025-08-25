import uuid

from django.contrib.auth.models import User
from django.db import models

from company.models import Company


# Create your models here.


class Partner(models.Model):
    partner_name = models.CharField(max_length=100)
    partner_street = models.CharField(max_length=100)
    partner_house_number = models.CharField(max_length=100)
    partner_city = models.CharField(max_length=100)
    partner_country = models.CharField(max_length=100)
    partner_phone = models.CharField(max_length=100)
    partner_email = models.EmailField(max_length=100)
    partner_zip = models.CharField(max_length=100)
    partner_created_at = models.DateTimeField(auto_now_add=True)
    partner_updated_at = models.DateTimeField(auto_now=True)
    partner_blocked = models.BooleanField(default=False)
    #partner_status
    partner_company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='partners', default=None)
    partner_owner = models.ManyToManyField(User, related_name='owned_partners')
    partner_staff = models.ManyToManyField(User, related_name='staff_partners', blank=True)
    def __str__(self):
        return self.partner_name

# erstell den serializer zu partner

class InvitationPartner(models.Model):
    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    email = models.EmailField()
    partner = models.ForeignKey(Partner, on_delete=models.CASCADE)
    invited_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    partner_to_create_used_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True,
                                                  related_name='invitation_invited_partner')


    def __str__(self):
        return f"Invitation for {self.email} to {self.partner.partner_name}"


class ExMembers(models.Model):
    partner = models.ForeignKey(Partner, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    executed_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="executer_partner")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.partner.partner_name}"


class Lead(models.Model):
    STATUS_CHOICES = [
        ('open', 'Offen'),
        ('won', 'Gewonnen'),
        ('lost', 'Verloren'),
    ]

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(max_length=100)
    phone = models.CharField(max_length=100)
    company = models.CharField(max_length=100)
    street = models.CharField(max_length=100)
    house_number = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    zip = models.CharField(max_length=100)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    blocked = models.BooleanField(default=False)

    partner = models.ForeignKey(Partner, on_delete=models.CASCADE, related_name='leads', default=None)
    creator = models.ManyToManyField(User, related_name='owned_leads')
    lead_uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    lead_note = models.TextField(max_length=1000, blank=True, null=True)
    lead_status = models.CharField(
        max_length=100,
        choices=STATUS_CHOICES,
        default='open'
    )

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.company}"

    def save(self, *args, **kwargs):
        if not self.lead_uuid:  # Setze die UUID nur, wenn sie nicht gesetzt ist
            self.lead_uuid = uuid.uuid4()
        super(Lead, self).save(*args, **kwargs)


class Contact(models.Model):
    contact_uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    contact_first_name = models.CharField(max_length=100)
    contact_last_name = models.CharField(max_length=100)
    contact_email = models.EmailField(max_length=100)
    contact_adress = models.CharField(max_length=100)
    contact_phonenumber = models.CharField(max_length=100)
    contact_note = models.TextField(max_length=1000, blank=True, null=True)
    contact_created_at = models.DateTimeField(auto_now_add=True)
    contact_updated_at = models.DateTimeField(auto_now=True)
    connected_lead = models.ManyToManyField(Lead, related_name='contacts')
    contact_status = models.CharField(
        max_length=100,

        default='open'
    )
    contact_creator = models.ManyToManyField(User, related_name='owned_contacts')
    contact_position = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.contact_first_name} {self.contact_last_name} - {self.contact_adress}"

    def save(self, *args, **kwargs):
        if not self.contact_uuid:
            self.contact_uuid = uuid.uuid4()
        super(Contact, self).save(*args, **kwargs)



