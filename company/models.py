import uuid

from django.db import models

# Create your models here.
from django.contrib.auth.models import User




class Company(models.Model):
    company_name = models.CharField(max_length=100)
    street = models.CharField(max_length=100)
    house_number = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    phone = models.CharField(max_length=100)
    email = models.EmailField(max_length=100)
    zip = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    blocked = models.BooleanField(default=False)


    owner = models.ManyToManyField(User, related_name='owned_companies')
    staff = models.ManyToManyField(User, related_name='staff_companies', blank=True)

    def __str__(self):
        return self.company_name





class CompanyRelationship(models.Model):
    from_company = models.ForeignKey(Company, related_name='outgoing_relationships', on_delete=models.CASCADE)
    to_company = models.ForeignKey(Company, related_name='incoming_relationships', on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.from_company} -> {self.to_company}"

class ExMembers(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    executed_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="executer_company", default=None)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.company.company_name}"

class InvitationCompany(models.Model):
    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    email = models.EmailField()
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    invited_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)
    company_used_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='invitations_company_used')
    def __str__(self):
        return f"Invitation for {self.email} to {self.company.company_name}"


class InvitationPartnerToCreate(models.Model):
    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    email = models.EmailField()
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    invited_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='invitations_sent')
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)
    partner_to_create_used_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True,
                                                  related_name='invitations_creater_partner')

    def __str__(self):
        return f"Invitation for {self.email} to {self.company.company_name}"
