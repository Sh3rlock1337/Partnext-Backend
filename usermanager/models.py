from django.contrib.auth.models import User
from django.db import models

class UserSettings(models.Model):
    LANGUAGE_CHOICES = [
        ('de', 'Deutsch'),
        ('en', 'English'),
        # Weitere Sprachen hier hinzufügen
    ]
    preferred_language = models.CharField(
        max_length=2,
        choices=LANGUAGE_CHOICES,
        default='de'
    )

    id = models.AutoField(primary_key=True)  # Auto incrementing primary key

    email_verified = models.BooleanField(default=False)  # 2FA
    otp = models.IntegerField(default=000000)
    is_company_owner = models.BooleanField(default=False)
    is_invited_user_company = models.BooleanField(default=False)
    is_invited_user_partner = models.BooleanField(default=False)
    os = models.CharField(max_length=15, default='')
    #connected_company

    customer_user = models.ForeignKey(User, on_delete=models.CASCADE)  # FK zu CustomerUser



