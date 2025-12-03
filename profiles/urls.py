from django.urls import path
from . import views

app_name = 'profiles'

urlpatterns = [
    path('onboarding/', views.OnboardingView.as_view(), name='onboarding'),
    path('student/', views.student_profile_view, name='student_profile'),
    path('teacher/', views.teacher_profile_view, name='teacher_profile'),
]

