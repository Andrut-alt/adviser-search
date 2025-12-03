from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages


def student_required(view_func):
    """Декоратор для перевірки, чи користувач є студентом"""
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('account_login')
        if not request.user.is_student:
            messages.error(request, "Ця сторінка доступна тільки для студентів.")
            if request.user.is_teacher:
                return redirect('profiles:teacher_profile')
            return redirect('profiles:onboarding')
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def teacher_required(view_func):
    """Декоратор для перевірки, чи користувач є викладачем"""
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('account_login')
        if not request.user.is_teacher:
            messages.error(request, "Ця сторінка доступна тільки для викладачів.")
            if request.user.is_student:
                return redirect('profiles:student_profile')
            return redirect('profiles:onboarding')
        return view_func(request, *args, **kwargs)
    return _wrapped_view

