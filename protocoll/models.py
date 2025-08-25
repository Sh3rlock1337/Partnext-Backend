from django.contrib.auth.models import User
from django.db import models

# Create your models here.
class Protocol(models.Model):
    ACTION_CHOICES = [
        ('CREATE', 'Create'),
        ('UPDATE', 'Update'),
        ('DELETE', 'Delete'),
        ('LOGIN', 'Login'),
        ('LOGOUT', 'Logout'),
        ('OTHER', 'Other'),
    ]

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=10, choices=ACTION_CHOICES)
    timestamp = models.DateTimeField(auto_now_add=True)  # Zeitstempel bei Erstellung
    description = models.TextField(blank=True, null=True)  # Optionaler Text für weitere Details
    #ip_address = models.GenericIPAddressField(null=True, blank=True)  # IP-Adresse, falls notwendig
    related_object = models.CharField(max_length=100, blank=True, null=True)  # Name des Objekts, auf das sich die Aktion bezieht (z.B. 'Company')

    def __str__(self):
        return f"{self.action} by {self.user} on {self.timestamp}"

    class Meta:
        verbose_name = 'Protocol'
        verbose_name_plural = 'Protocols'
        ordering = ['-timestamp']