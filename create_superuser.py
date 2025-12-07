import os
import django
from django.conf import settings

# 1. Налаштовуємо середовище Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mentorion.settings")
django.setup()

from django.contrib.auth import get_user_model

def create_admin():
    User = get_user_model()
    
   
    my_email = "voloshyn.andriy2006@gmail.com"
    my_password = "Wertyk02" 
  

   
    if not User.objects.filter(email=my_email).exists():
        print(f"Створення суперюзера {my_email}...")
        try:
            u = User.objects.create_superuser(
                email=my_email, 
                password=my_password,
               \
                username=my_email.split('@')[0] if hasattr(User, 'username') else None
            )
            print("СУПЕРЮЗЕРА УСПІШНО СТВОРЕНО! :)")
        except Exception as e:
            print(f"Помилка при створенні: {e}")
    else:
        print("Суперюзер з таким email вже існує.")

if __name__ == "__main__":
    create_admin()
    