from django.contrib.auth.models import User
from django.db import models

from company.models import Company


class Group(models.Model):
    name = models.CharField(max_length=100, null=False)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="groups", default=None)
    members = models.ManyToManyField(User, related_name="custom_groups", blank=False)

    def __str__(self):
        return f"{self.name} - {self.company.name}"

class Permission(models.Model):
    name = models.CharField(max_length=100, null=False)
    description = models.TextField(blank=True)
    module = models.CharField(max_length=100, default=None)
    groups = models.ManyToManyField(Group, related_name="permissions", blank=False)

    def __str__(self):
        return self.name