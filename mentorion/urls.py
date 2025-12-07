"""Main URL configuration for the Mentorion project."""

from django.contrib import admin
from django.shortcuts import redirect
from django.urls import include, path

from profiles.models import StudentProfile, TeacherProfile


def home(request):
    """
    Home view that redirects users based on authentication and profile status.

    Redirects:
    - Authenticated users with student profile -> student profile page
    - Authenticated users with teacher profile -> teacher profile page
    - Authenticated users without profile -> onboarding page
    - Unauthenticated users -> login page

    Args:
        request: HTTP request object.

    Returns:
        HttpResponse: Redirect to appropriate page.
    """
    if not request.user.is_authenticated:
        return redirect('account_login')

    if StudentProfile.objects.filter(user=request.user).exists():
        return redirect('profiles:student_profile')

    if TeacherProfile.objects.filter(user=request.user).exists():
        return redirect('profiles:teacher_profile')

    return redirect('profiles:onboarding')


urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("allauth.urls")),
    path("profiles/", include("profiles.urls")),
    path("searching/", include("searching.urls")),
    path("", home, name="home"),
]
