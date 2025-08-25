from usermanager.models import UserSettings

from simpleapi.views import language_manager



def checkForUser(user):
    if user.is_authenticated:
        if user.is_active:
            usersettings = UserSettings.objects.get(customer_user=user)
            preffered_language = usersettings.preferred_language

            if usersettings.email_verified:
                return True
            else:
                email_not_verified = language_manager.get_text(preffered_language, 'email_not_verified')
                return {"message": email_not_verified}
        else:
            usersettings = UserSettings.objects.get(customer_user=user)
            preffered_language = usersettings.preferred_language
            company_blocked = language_manager.get_text(preffered_language, 'company_blocked')
            return {"message": company_blocked}

    else:
        return {"message": "User is not authenticated"}