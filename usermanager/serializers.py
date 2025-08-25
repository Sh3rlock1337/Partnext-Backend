from rest_framework import generics, permissions, serializers

from usermanager.models import UserSettings


class userSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserSettings
        fields = ('username', 'email', "first_name", "last_name")
