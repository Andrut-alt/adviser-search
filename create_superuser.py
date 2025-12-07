import os
import django
from django.conf import settings

# 1. Налаштовуємо середовище Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mentorion.settings")
django.setup()

from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site

def init_data():
    print("Перевірка налаштувань сайту (Site ID)...")
    try:
        site, created = Site.objects.update_or_create(
            pk=1,
            defaults={
                'domain': 'mentorion.onrender.com', 
                'name': 'Mentorion'
            }
        )
        print(f"Сайт успішно налаштовано: ID={site.id}, Domain={site.domain}")
    except Exception as e:
        print(f"Помилка при налаштуванні сайту: {e}")

    User = get_user_model()
    my_email = "voloshyn.andriy2006@gmail.com"
    my_password = "Wertyk02"

    if not User.objects.filter(email=my_email).exists():
        print(f"Створення суперюзера {my_email}...")
        try:
            User.objects.create_superuser(
                email=my_email, 
                password=my_password,
            )
            print("СУПЕРЮЗЕРА УСПІШНО СТВОРЕНО!")
        except Exception as e:
            print(f"Помилка при створенні юзера: {e}")
    else:
        print("Суперюзер вже існує.")

if __name__ == "__main__":
    init_data()