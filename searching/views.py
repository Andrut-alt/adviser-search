from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from profiles.models import TeacherProfile
from profiles.decorators import student_required, teacher_required
from .models import Slot, SlotRequest


@login_required
@student_required
def filter_teachers_view(request):
    """Список викладачів з фільтрацією"""
    student_profile = request.user.student_profile
    # Тільки підтверджені викладачі
    teachers = TeacherProfile.objects.filter(is_approved=True)
    
    # Фільтрація за кафедрою
    department_id = request.GET.get('department')
    if department_id:
        teachers = teachers.filter(department_id=department_id)
    
    # Фільтрація за науковими інтересами
    interest_id = request.GET.get('interest')
    if interest_id:
        teachers = teachers.filter(scientific_interests__id=interest_id)
    
    # Обмеження: для студентів 3-4 курсу - тільки викладачі зі своєї кафедри
    if student_profile.year_of_study in [3, 4] and student_profile.department:
        teachers = teachers.filter(department=student_profile.department)
    
    # Унікальність (на випадок фільтрації за інтересами)
    teachers = teachers.distinct()
    
    # Імпорт Department для форми фільтрації
    from profiles.models import Department, ScientificInterest
    departments = Department.objects.all()
    interests = ScientificInterest.objects.all()
    
    context = {
        'teachers': teachers,
        'departments': departments,
        'interests': interests,
        'selected_department': department_id,
        'selected_interest': interest_id,
    }
    return render(request, 'searching/filter_teachers.html', context)


@login_required
@student_required
def teacher_detail_view(request, teacher_id):
    """Детальний профіль викладача для студента"""
    teacher = get_object_or_404(TeacherProfile, id=teacher_id)
    student_profile = request.user.student_profile
    
    # Отримуємо вільні слоти
    available_slots = teacher.slots.filter(is_available=True, is_filled=False)
    first_available_slot = available_slots.first()
    
    # Перевіряємо, чи є активний запит від цього студента
    active_request = SlotRequest.objects.filter(
        student=student_profile,
        slot__teacher=teacher,
        status='pending'
    ).first()
    
    # Перевіряємо, чи є прикріплений слот
    has_assigned_slot = Slot.objects.filter(student=student_profile, is_filled=True).exists()
    
    context = {
        'teacher': teacher,
        'available_slots': available_slots,
        'first_available_slot': first_available_slot,
        'active_request': active_request,
        'has_assigned_slot': has_assigned_slot,
        'can_send_request': not active_request and not has_assigned_slot and available_slots.exists(),
    }
    return render(request, 'searching/teacher_detail.html', context)


@login_required
@student_required
def send_slot_request_view(request, slot_id):
    """Надсилання запиту на слот"""
    slot = get_object_or_404(Slot, id=slot_id)
    student_profile = request.user.student_profile
    
    # Валідація
    if slot.is_filled or not slot.is_available:
        messages.error(request, "Цей слот вже зайнятий.")
        return redirect('searching:teacher_detail', teacher_id=slot.teacher.id)
    
    # Перевірка активних запитів
    active_request = SlotRequest.objects.filter(
        student=student_profile,
        status='pending'
    ).first()
    
    if active_request:
        messages.error(request, "У вас вже є активний запит. Спочатку дочекайтеся відповіді.")
        return redirect('profiles:student_profile')
    
    # Перевірка прикріпленого слота
    if Slot.objects.filter(student=student_profile, is_filled=True).exists():
        messages.error(request, "Ви вже прикріплені до викладача.")
        return redirect('profiles:student_profile')
    
    # Створення запиту
    message = request.POST.get('message', '')
    SlotRequest.objects.create(
        student=student_profile,
        slot=slot,
        status='pending',
        message=message
    )
    
    messages.success(request, "Запит успішно надіслано!")
    return redirect('profiles:student_profile')


@login_required
@teacher_required
def teacher_requests_view(request):
    """Список запитів до слотів викладача"""
    teacher_profile = request.user.teacher_profile
    
    # Отримуємо всі запити до слотів цього викладача
    requests = SlotRequest.objects.filter(
        slot__teacher=teacher_profile
    ).order_by('-created_at')
    
    context = {
        'requests': requests,
    }
    return render(request, 'searching/teacher_requests.html', context)


@login_required
@teacher_required
def approve_request_view(request, request_id):
    """Підтвердження запиту"""
    slot_request = get_object_or_404(SlotRequest, id=request_id)
    
    # Перевірка власності
    if slot_request.slot.teacher != request.user.teacher_profile:
        messages.error(request, "Ви не маєте доступу до цього запиту.")
        return redirect('searching:teacher_requests')
    
    # Перевірка статусу
    if slot_request.status != 'pending':
        messages.error(request, "Цей запит вже оброблено.")
        return redirect('searching:teacher_requests')
    
    # Перевірка заповненості слота
    if slot_request.slot.is_filled:
        messages.error(request, "Цей слот вже зайнятий.")
        return redirect('searching:teacher_requests')
    
    # Підтвердження запиту
    slot_request.slot.student = slot_request.student
    slot_request.slot.is_filled = True
    slot_request.slot.is_available = False
    slot_request.slot.save()
    
    slot_request.status = 'approved'
    slot_request.save()
    
    # Відхиляємо інші pending запити на цей слот
    SlotRequest.objects.filter(
        slot=slot_request.slot,
        status='pending'
    ).exclude(id=request_id).update(status='rejected')
    
    messages.success(request, "Запит підтверджено!")
    return redirect('searching:teacher_requests')


@login_required
@teacher_required
def reject_request_view(request, request_id):
    """Відхилення запиту"""
    slot_request = get_object_or_404(SlotRequest, id=request_id)
    
    # Перевірка власності
    if slot_request.slot.teacher != request.user.teacher_profile:
        messages.error(request, "Ви не маєте доступу до цього запиту.")
        return redirect('searching:teacher_requests')
    
    # Перевірка статусу
    if slot_request.status != 'pending':
        messages.error(request, "Цей запит вже оброблено.")
        return redirect('searching:teacher_requests')
    
    # Відхилення запиту
    slot_request.status = 'rejected'
    slot_request.save()
    
    messages.success(request, "Запит відхилено.")
    return redirect('searching:teacher_requests')


@login_required
@teacher_required
def teacher_slots_view(request):
    """Список слотів викладача"""
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
    """Створення нового слота"""
    teacher_profile = request.user.teacher_profile
    
    # Перевірка максимальної кількості слотів
    if teacher_profile.slots.count() >= teacher_profile.max_slots:
        messages.error(request, "Досягнуто максимальну кількість слотів.")
        return redirect('searching:teacher_slots')
    
    # Створення слота
    Slot.objects.create(teacher=teacher_profile)
    messages.success(request, "Слот успішно створено!")
    return redirect('searching:teacher_slots')


@login_required
@teacher_required
def delete_slot_view(request, slot_id):
    """Видалення слота"""
    slot = get_object_or_404(Slot, id=slot_id)
    
    # Перевірка власності
    if slot.teacher != request.user.teacher_profile:
        messages.error(request, "Ви не маєте доступу до цього слота.")
        return redirect('searching:teacher_slots')
    
    # Перевірка заповненості
    if slot.is_filled:
        messages.error(request, "Неможливо видалити зайнятий слот.")
        return redirect('searching:teacher_slots')
    
    # Видалення слота
    slot.delete()
    messages.success(request, "Слот успішно видалено!")
    return redirect('searching:teacher_slots')


@login_required
@teacher_required
def slot_detail_view(request, slot_id):
    """Детальна інформація про слот"""
    slot = get_object_or_404(Slot, id=slot_id)
    
    # Перевірка власності
    if slot.teacher != request.user.teacher_profile:
        messages.error(request, "Ви не маєте доступу до цього слота.")
        return redirect('searching:teacher_slots')
    
    # Отримуємо історію запитів
    requests = slot.requests.all().order_by('-created_at')
    
    context = {
        'slot': slot,
        'requests': requests,
    }
    return render(request, 'searching/slot_detail.html', context)
