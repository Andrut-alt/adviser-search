from django.contrib import admin
from .models import Department, ScientificInterest, StudentProfile, TeacherProfile


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(ScientificInterest)
class ScientificInterestAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name', 'description')


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'group', 'year_of_study', 'department', 'course_topic')
    list_filter = ('year_of_study', 'department')
    search_fields = ('user__email', 'user__first_name', 'user__last_name', 'group', 'course_topic')
    readonly_fields = ('user',)


@admin.register(TeacherProfile)
class TeacherProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'department', 'is_approved', 'max_slots', 'total_slots_display', 'available_slots_display')
    list_filter = ('department', 'is_approved')
    search_fields = ('user__email', 'user__first_name', 'user__last_name')
    readonly_fields = ('user', 'approved_by', 'approved_at')
    filter_horizontal = ('scientific_interests',)
    actions = ['approve_teachers']
    
    def total_slots_display(self, obj):
        return obj.total_slots_count()
    total_slots_display.short_description = 'Всього слотів'
    
    def available_slots_display(self, obj):
        return obj.available_slots_count()
    available_slots_display.short_description = 'Вільних слотів'
    
    def approve_teachers(self, request, queryset):
        """Дія для апруву викладачів"""
        from django.utils import timezone
        
        updated = 0
        for teacher in queryset.filter(is_approved=False):
            teacher.is_approved = True
            teacher.approved_by = request.user
            teacher.approved_at = timezone.now()
            teacher.save()
            updated += 1
        
        self.message_user(request, f'Підтверджено {updated} викладачів.')
    approve_teachers.short_description = 'Підтвердити обраних викладачів'

