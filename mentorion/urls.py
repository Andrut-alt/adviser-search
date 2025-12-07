from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse
from django.shortcuts import redirect

def home(request):
    # Діагностика: перевіряємо стан користувача
    if request.user.is_authenticated:
        # Перевіряємо наявність профілю безпосередньо через модель
        from profiles.models import StudentProfile, TeacherProfile
        
        # Перевіряємо, чи є профіль студента
        if StudentProfile.objects.filter(user=request.user).exists():
            return redirect('profiles:student_profile')
        
        # Перевіряємо, чи є профіль викладача
        if TeacherProfile.objects.filter(user=request.user).exists():
            return redirect('profiles:teacher_profile')
        
        # Якщо профілю немає, редіректимо на onboarding
        return redirect('profiles:onboarding')
    
    # Якщо користувач не автентифікований - редіректимо на сторінку входу
    return redirect('account_login')

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("allauth.urls")),  # дає /accounts/login/, /accounts/microsoft/ тощо
    path("profiles/", include("profiles.urls")),
    path("searching/", include("searching.urls")),
    path("dev-login/", lambda request: __import__('users.views', fromlist=['dev_login']).dev_login(request), name="dev_login"),  # Тільки для розробки!
    path("", home, name="home"),
]
