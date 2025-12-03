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
    list_display = ('user', 'department', 'max_slots', 'total_slots_display', 'available_slots_display')
    list_filter = ('department',)
    search_fields = ('user__email', 'user__first_name', 'user__last_name')
    readonly_fields = ('user',)
    filter_horizontal = ('scientific_interests',)
    
    def total_slots_display(self, obj):
        return obj.total_slots_count()
    total_slots_display.short_description = 'Всього слотів'
    
    def available_slots_display(self, obj):
        return obj.available_slots_count()
    available_slots_display.short_description = 'Вільних слотів'
