# users/signals.py
from allauth.account.signals import user_signed_up
from django.dispatch import receiver
from django.contrib.auth import get_user_model

User = get_user_model()


@receiver(user_signed_up)
def populate_user_from_socialaccount(sender, request, user, **kwargs):
    """Витягує first_name та last_name з Microsoft OAuth при реєстрації"""
    try:
        socialaccount = user.socialaccount_set.filter(provider='microsoft').first()
        if socialaccount:
            extra_data = socialaccount.extra_data
            # Microsoft повертає дані в різних форматах
            if 'givenName' in extra_data and not user.first_name:
                user.first_name = extra_data.get('givenName', '')
            if 'surname' in extra_data and not user.last_name:
                user.last_name = extra_data.get('surname', '')
            # Альтернативно, можна використовувати displayName
            if 'displayName' in extra_data and not user.first_name and not user.last_name:
                display_name = extra_data.get('displayName', '')
                if display_name:
                    parts = display_name.split(' ', 1)
                    if len(parts) >= 1:
                        user.first_name = parts[0]
                    if len(parts) >= 2:
                        user.last_name = parts[1]
            user.save()
    except Exception:
        # Якщо виникла помилка, просто ігноруємо її
        pass
