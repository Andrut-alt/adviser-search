from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse

def home(_):
    return HttpResponse("OK. Ви увійшли. <a href='/accounts/logout/'>Вийти</a>")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("allauth.urls")),  # дає /accounts/login/, /accounts/microsoft/ тощо
    path("", home, name="home"),
]
