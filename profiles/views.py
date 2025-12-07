from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import FormView
from django.urls import reverse_lazy
from django.contrib import messages
from .forms import OnboardingForm
from .decorators import student_required, teacher_required


@method_decorator(login_required, name="dispatch")
class OnboardingView(FormView):
    template_name = "profiles/onboarding.html"
    form_class = OnboardingForm

    def dispatch(self, request, *args, **kwargs):
        # Якщо профіль вже створений, редіректимо на відповідний dashboard
        if request.user.has_profile:
            if request.user.is_student:
                return redirect('profiles:student_profile')
            elif request.user.is_teacher:
                return redirect('profiles:teacher_profile')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        # Створюємо профіль
        profile = form.save(self.request.user)
        messages.success(self.request, "Профіль успішно створено!")
        
        # Редіректимо на відповідний dashboard
        if profile.__class__.__name__ == 'StudentProfile':
            return redirect('profiles:student_profile')
        elif profile.__class__.__name__ == 'TeacherProfile':
            return redirect('profiles:teacher_profile')
        
        return redirect('home')


@login_required
@student_required
def student_profile_view(request):
    """Профіль студента"""
    student_profile = request.user.student_profile
    
    # Отримуємо активний запит (якщо є)
    active_request = student_profile.slot_requests.filter(status='pending').first()
    
    # Отримуємо прикріплений слот (якщо є)
    from searching.models import Slot
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
    """Профіль викладача"""
    teacher_profile = request.user.teacher_profile
    
    context = {
        'teacher_profile': teacher_profile,
        'total_slots': teacher_profile.total_slots_count(),
        'available_slots': teacher_profile.available_slots_count(),
        'filled_slots': teacher_profile.filled_slots_count(),
        'is_approved': teacher_profile.is_approved,
    }
    return render(request, 'profiles/teacher_profile.html', context)

