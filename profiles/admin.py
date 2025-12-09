"""Django admin configuration for profile models."""

from django.contrib import admin
from django.utils import timezone

from .models import Department, ScientificInterest, StudentProfile, TeacherProfile
from django.http import HttpResponse
from io import BytesIO
import csv


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    """Admin interface for Department model."""

    list_display = ('name',)
    search_fields = ('name',)


@admin.register(ScientificInterest)
class ScientificInterestAdmin(admin.ModelAdmin):
    """Admin interface for ScientificInterest model."""

    list_display = ('name', 'description')
    search_fields = ('name', 'description')


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    """Admin interface for StudentProfile model."""

    list_display = ('user', 'group', 'year_of_study', 'department', 'course_topic')
    list_filter = ('year_of_study', 'department')
    search_fields = ('user__email', 'user__first_name', 'user__last_name', 'group', 'course_topic')
    readonly_fields = ('user',)

    actions = ['export_students_excel']

    def export_students_excel(self, request, queryset):
        """
        Export selected student profiles to an Excel file (XLSX). Falls back to CSV if openpyxl
        is not installed.
        """
        # Try XLSX via openpyxl
        try:
            from openpyxl import Workbook
        except Exception:
            # Fallback to CSV
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename=students_export.csv'
            writer = csv.writer(response)
            writer.writerow(['Студент', 'Група', 'Кафедра', 'Викладач, якщо вже узгоджено', 'Тема курсової'])
            for sp in queryset:
                student = f"{sp.user.last_name} {sp.user.first_name} ({sp.user.email})"
                group = sp.group
                dept = sp.department.name if sp.department else ''
                teacher = ''
                topic = ''
                if hasattr(sp, 'assigned_slot') and sp.assigned_slot:
                    slot = sp.assigned_slot
                    teacher_profile = slot.teacher
                    teacher = f"{teacher_profile.user.last_name} {teacher_profile.user.first_name} ({teacher_profile.user.email})"
                    topic = slot.topic if getattr(slot, 'topic', None) else (sp.course_topic or '')
                else:
                    topic = sp.course_topic or ''
                writer.writerow([student, group, dept, teacher, topic])
            return response

        wb = Workbook()
        ws = wb.active
        ws.title = 'Students'
        headers = ['Студент', 'Група', 'Кафедра', 'Викладач, якщо вже узгоджено', 'Тема курсової / побажання']
        ws.append(headers)

        for sp in queryset:
            student = f"{sp.user.last_name} {sp.user.first_name} ({sp.user.email})"
            group = sp.group
            dept = sp.department.name if sp.department else ''
            teacher = ''
            topic = ''
            if hasattr(sp, 'assigned_slot') and sp.assigned_slot:
                slot = sp.assigned_slot
                teacher_profile = slot.teacher
                teacher = f"{teacher_profile.user.last_name} {teacher_profile.user.first_name} ({teacher_profile.user.email})"
                topic = slot.topic if getattr(slot, 'topic', None) else (sp.course_topic or '')
            else:
                topic = sp.course_topic or ''
            ws.append([student, group, dept, teacher, topic])

        output = BytesIO()
        wb.save(output)
        output.seek(0)

        response = HttpResponse(output.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename=students_export.xlsx'
        return response

    export_students_excel.short_description = 'Експорт вибраних студентів в Excel'


@admin.register(TeacherProfile)
class TeacherProfileAdmin(admin.ModelAdmin):
    """Admin interface for TeacherProfile model with approval functionality."""

    list_display = ('user', 'department', 'is_approved', 'max_slots', 'total_slots_display', 'available_slots_display')
    list_filter = ('department', 'is_approved')
    search_fields = ('user__email', 'user__first_name', 'user__last_name')
    readonly_fields = ('user', 'approved_by', 'approved_at')
    filter_horizontal = ('scientific_interests',)
    actions = ['approve_teachers']

    def total_slots_display(self, obj):
        """Display total number of slots."""
        return obj.total_slots_count()
    total_slots_display.short_description = 'Всього слотів'

    def available_slots_display(self, obj):
        """Display number of available slots."""
        return obj.available_slots_count()
    available_slots_display.short_description = 'Вільних слотів'

    def approve_teachers(self, request, queryset):
        """
        Admin action to approve selected teachers.

        Args:
            request: HTTP request object.
            queryset: QuerySet of selected TeacherProfile instances.
        """
        updated = 0
        for teacher in queryset.filter(is_approved=False):
            teacher.is_approved = True
            teacher.approved_by = request.user
            teacher.approved_at = timezone.now()
            teacher.save()
            updated += 1

        self.message_user(request, f'Підтверджено {updated} викладачів.')
    approve_teachers.short_description = 'Підтвердити обраних викладачів'
