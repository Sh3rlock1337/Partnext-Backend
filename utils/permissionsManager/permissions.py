import jwt
from django.conf import settings
from datetime import datetime, timedelta

def generate_jwt(user):
    payload = {
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'user_id': user.id,
        'is_staff': user.is_staff,
        'is_superuser': user.is_superuser,
        'exp': datetime.utcnow() + timedelta(hours=1)  # Beispiel für 1 Tag gültig
    }
    token = jwt.encode(payload, settings.JWT_TOKEN, algorithm='HS256')
    return token




