from django.contrib import admin
from .models import Slot, SlotRequest


@admin.register(Slot)
class SlotAdmin(admin.ModelAdmin):
    list_display = ('id', 'teacher', 'student', 'is_available', 'is_filled', 'created_at')
    list_filter = ('is_available', 'is_filled', 'created_at')
    search_fields = ('teacher__user__email', 'student__user__email')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(SlotRequest)
class SlotRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'student', 'slot', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('student__user__email', 'slot__teacher__user__email')
    readonly_fields = ('created_at', 'updated_at')
