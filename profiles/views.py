"""Profile views for onboarding and profile management."""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils.decorators import method_decorator
from django.views.generic import FormView

from searching.models import Slot

from .decorators import student_required, teacher_required
from .forms import OnboardingForm


@method_decorator(login_required, name="dispatch")
class OnboardingView(FormView):
    """
    View for user onboarding to create student or teacher profile.

    Redirects to appropriate profile page if profile already exists.
    """

    template_name = "profiles/onboarding.html"
    form_class = OnboardingForm

    def dispatch(self, request, *args, **kwargs):
        """
        Check if user already has a profile and redirect accordingly.

        Args:
            request: HTTP request object.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            HttpResponse: Redirect to profile page or onboarding form.
        """
        if request.user.has_profile:
            if request.user.is_student:
                return redirect('profiles:student_profile')
            if request.user.is_teacher:
                return redirect('profiles:teacher_profile')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        """
        Handle valid form submission by creating profile.

        Args:
            form: Valid OnboardingForm instance.

        Returns:
            HttpResponse: Redirect to appropriate profile page.
        """
        profile = form.save(self.request.user)
        messages.success(self.request, "Профіль успішно створено!")

        if profile.__class__.__name__ == 'StudentProfile':
            return redirect('profiles:student_profile')
        if profile.__class__.__name__ == 'TeacherProfile':
            return redirect('profiles:teacher_profile')

        return redirect('home')


@login_required
@student_required
def student_profile_view(request):
    """
    Display student profile with active requests and assigned teacher.

    Args:
        request: HTTP request object.

    Returns:
        HttpResponse: Rendered student profile page.
    """
    student_profile = request.user.student_profile

    active_request = student_profile.slot_requests.filter(status='pending').first()
    assigned_slot = Slot.objects.filter(student=student_profile, is_filled=True).first()
    teacher = assigned_slot.teacher if assigned_slot else None

    context = {
        'student_profile': student_profile,
        'active_request': active_request,
        'assigned_slot': assigned_slot,
        'teacher': teacher,
    }
    return render(request, 'profiles/student_profile.html', context)


@login_required
@teacher_required
def teacher_profile_view(request):
    """
    Display teacher profile with slot statistics and approval status.

    Args:
        request: HTTP request object.

    Returns:
        HttpResponse: Rendered teacher profile page.
    """
    teacher_profile = request.user.teacher_profile

    context = {
        'teacher_profile': teacher_profile,
        'total_slots': teacher_profile.total_slots_count(),
        'available_slots': teacher_profile.available_slots_count(),
        'filled_slots': teacher_profile.filled_slots_count(),
        'is_approved': teacher_profile.is_approved,
    }
    return render(request, 'profiles/teacher_profile.html', context)
