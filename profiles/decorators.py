"""Decorators for role-based access control."""

from functools import wraps

from django.contrib import messages
from django.shortcuts import redirect


def student_required(view_func):
    """
    Decorator to restrict view access to students only.

    Args:
        view_func: View function to wrap.

    Returns:
        Wrapped view function that checks for student role.
    """
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
    """
    Decorator to restrict view access to teachers only.

    Args:
        view_func: View function to wrap.

    Returns:
        Wrapped view function that checks for teacher role.
    """
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
