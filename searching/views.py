"""Views for teacher search, slot management, and request handling."""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from profiles.decorators import student_required, teacher_required
from profiles.models import Department, ScientificInterest, TeacherProfile

from .models import Slot, SlotRequest


@login_required
@student_required
def filter_teachers_view(request):
    """
    Display filtered list of approved teachers for students.

    Filters:
    - Only approved teachers
    - By department (optional)
    - By scientific interests (optional)
    - 3rd/4th year students: only teachers from their department

    Args:
        request: HTTP request object.

    Returns:
        HttpResponse: Rendered teacher list page.
    """
    student_profile = request.user.student_profile
    teachers = TeacherProfile.objects.filter(is_approved=True)

    department_id = request.GET.get('department')
    if department_id:
        teachers = teachers.filter(department_id=department_id)

    interest_id = request.GET.get('interest')
    if interest_id:
        teachers = teachers.filter(scientific_interests__id=interest_id)

    if student_profile.year_of_study in [3, 4] and student_profile.department:
        teachers = teachers.filter(department=student_profile.department)

    teachers = teachers.distinct()

    context = {
        'teachers': teachers,
        'departments': Department.objects.all(),
        'interests': ScientificInterest.objects.all(),
        'selected_department': department_id,
        'selected_interest': interest_id,
        'student_profile': student_profile,
        'hide_department_filter': student_profile.year_of_study in [3, 4],
    }
    return render(request, 'searching/filter_teachers.html', context)


@login_required
@student_required
def teacher_detail_view(request, teacher_id):
    """
    Display detailed teacher profile with available slots.

    Args:
        request: HTTP request object.
        teacher_id: ID of the teacher to display.

    Returns:
        HttpResponse: Rendered teacher detail page.
    """
    teacher = get_object_or_404(TeacherProfile, id=teacher_id)
    student_profile = request.user.student_profile

    # For 3rd/4th year students restrict access to teachers from their department only
    if student_profile.year_of_study in [3, 4] and student_profile.department:
        if teacher.department != student_profile.department:
            messages.error(request, "Ви можете переглядати лише викладачів своєї кафедри.")
            return redirect('searching:filter_teachers')

    available_slots = teacher.slots.filter(is_available=True, is_filled=False)
    active_request = SlotRequest.objects.filter(
        student=student_profile,
        slot__teacher=teacher,
        status='pending'
    ).first()
    has_assigned_slot = Slot.objects.filter(student=student_profile, is_filled=True).exists()

    context = {
        'teacher': teacher,
        'available_slots': available_slots,
        'first_available_slot': available_slots.first(),
        'active_request': active_request,
        'has_assigned_slot': has_assigned_slot,
        'can_send_request': not active_request and not has_assigned_slot and available_slots.exists(),
    }
    return render(request, 'searching/teacher_detail.html', context)


@login_required
@student_required
def send_slot_request_view(request, slot_id):
    """
    Send a request for a consultation slot.

    Validates:
    - Slot is available and not filled
    - Student has no active requests
    - Student is not already assigned to a teacher

    Args:
        request: HTTP request object.
        slot_id: ID of the slot to request.

    Returns:
        HttpResponse: Redirect to student profile or teacher detail.
    """
    slot = get_object_or_404(Slot, id=slot_id)
    student_profile = request.user.student_profile

    if student_profile.year_of_study in [3, 4] and student_profile.department:
        teacher = slot.teacher
        if teacher.department != student_profile.department:
            messages.error(request, "Студенти 3-4 курсу можуть надсилати запити лише викладачам своєї кафедри.")
            return redirect('searching:filter_teachers')

    if slot.is_filled or not slot.is_available:
        messages.error(request, "Цей слот вже зайнятий.")
        return redirect('searching:teacher_detail', teacher_id=slot.teacher.id)

    if SlotRequest.objects.filter(student=student_profile, status='pending').exists():
        messages.error(request, "У вас вже є активний запит. Спочатку дочекайтеся відповіді.")
        return redirect('profiles:student_profile')

    if Slot.objects.filter(student=student_profile, is_filled=True).exists():
        messages.error(request, "Ви вже прикріплені до викладача.")
        return redirect('profiles:student_profile')

    SlotRequest.objects.create(
        student=student_profile,
        slot=slot,
        status='pending',
        message=request.POST.get('message', '')
    )

    messages.success(request, "Запит успішно надіслано!")
    return redirect('profiles:student_profile')


@login_required
@teacher_required
def teacher_requests_view(request):
    """
    Display all slot requests for the teacher.

    Args:
        request: HTTP request object.

    Returns:
        HttpResponse: Rendered requests list page.
    """
    teacher_profile = request.user.teacher_profile
    requests = SlotRequest.objects.filter(
        slot__teacher=teacher_profile
    ).order_by('-created_at')

    context = {'requests': requests}
    return render(request, 'searching/teacher_requests.html', context)


@login_required
@teacher_required
def approve_request_view(request, request_id):
    """
    Approve a student's slot request.

    Validates:
    - Teacher owns the slot
    - Request is pending
    - Slot is not already filled

    Args:
        request: HTTP request object.
        request_id: ID of the request to approve.

    Returns:
        HttpResponse: Redirect to teacher requests page.
    """
    slot_request = get_object_or_404(SlotRequest, id=request_id)

    if slot_request.slot.teacher != request.user.teacher_profile:
        messages.error(request, "Ви не маєте доступу до цього запиту.")
        return redirect('searching:teacher_requests')

    if slot_request.status != 'pending':
        messages.error(request, "Цей запит вже оброблено.")
        return redirect('searching:teacher_requests')

    if slot_request.slot.is_filled:
        messages.error(request, "Цей слот вже зайнятий.")
        return redirect('searching:teacher_requests')

    slot_request.slot.student = slot_request.student
    slot_request.slot.is_filled = True
    slot_request.slot.is_available = False
    slot_request.slot.save()

    slot_request.status = 'approved'
    slot_request.save()

    SlotRequest.objects.filter(
        slot=slot_request.slot,
        status='pending'
    ).exclude(id=request_id).update(status='rejected')

    messages.success(request, "Запит підтверджено!")
    return redirect('searching:teacher_requests')


@login_required
@teacher_required
def reject_request_view(request, request_id):
    """
    Reject a student's slot request.

    Args:
        request: HTTP request object.
        request_id: ID of the request to reject.

    Returns:
        HttpResponse: Redirect to teacher requests page.
    """
    slot_request = get_object_or_404(SlotRequest, id=request_id)

    if slot_request.slot.teacher != request.user.teacher_profile:
        messages.error(request, "Ви не маєте доступу до цього запиту.")
        return redirect('searching:teacher_requests')

    if slot_request.status != 'pending':
        messages.error(request, "Цей запит вже оброблено.")
        return redirect('searching:teacher_requests')

    slot_request.status = 'rejected'
    slot_request.save()

    messages.success(request, "Запит відхилено.")
    return redirect('searching:teacher_requests')


@login_required
@teacher_required
def teacher_slots_view(request):
    """
    Display all slots for the teacher with creation capability.

    Args:
        request: HTTP request object.

    Returns:
        HttpResponse: Rendered slots list page.
    """
    teacher_profile = request.user.teacher_profile
    slots = teacher_profile.slots.all().order_by('-created_at')

    context = {
        'slots': slots,
        'max_slots': teacher_profile.max_slots,
        'can_create_slot': slots.count() < teacher_profile.max_slots,
        'remaining_slots': teacher_profile.max_slots - slots.count(),
    }
    return render(request, 'searching/teacher_slots.html', context)


@login_required
@teacher_required
def create_slot_view(request):
    """
    Create a new consultation slot for the teacher.

    Args:
        request: HTTP request object.

    Returns:
        HttpResponse: Redirect to teacher slots page.
    """
    teacher_profile = request.user.teacher_profile

    if teacher_profile.slots.count() >= teacher_profile.max_slots:
        messages.error(request, "Досягнуто максимальну кількість слотів.")
        return redirect('searching:teacher_slots')

    Slot.objects.create(teacher=teacher_profile)
    messages.success(request, "Слот успішно створено!")
    return redirect('searching:teacher_slots')


@login_required
@teacher_required
def delete_slot_view(request, slot_id):
    """
    Delete an unfilled consultation slot.

    Args:
        request: HTTP request object.
        slot_id: ID of the slot to delete.

    Returns:
        HttpResponse: Redirect to teacher slots page.
    """
    slot = get_object_or_404(Slot, id=slot_id)

    if slot.teacher != request.user.teacher_profile:
        messages.error(request, "Ви не маєте доступу до цього слота.")
        return redirect('searching:teacher_slots')

    if slot.is_filled:
        messages.error(request, "Неможливо видалити зайнятий слот.")
        return redirect('searching:teacher_slots')

    slot.delete()
    messages.success(request, "Слот успішно видалено!")
    return redirect('searching:teacher_slots')


@login_required
@teacher_required
def slot_detail_view(request, slot_id):
    """
    Display detailed information about a slot and its requests.

    Args:
        request: HTTP request object.
        slot_id: ID of the slot to display.

    Returns:
        HttpResponse: Rendered slot detail page.
    """
    slot = get_object_or_404(Slot, id=slot_id)

    if slot.teacher != request.user.teacher_profile:
        messages.error(request, "Ви не маєте доступу до цього слота.")
        return redirect('searching:teacher_slots')

    requests = slot.requests.all().order_by('-created_at')

    context = {
        'slot': slot,
        'requests': requests,
    }
    return render(request, 'searching/slot_detail.html', context)
