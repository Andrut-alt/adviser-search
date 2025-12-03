# profiles/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import TeacherProfile


@receiver(post_save, sender=TeacherProfile)
def create_slots_for_teacher(sender, instance: TeacherProfile, created: bool, **kwargs):
    """Автоматично створює слоти для викладача при створенні профілю"""
    if created:
        from searching.models import Slot
        # Створюємо слоти згідно з max_slots
        for i in range(instance.max_slots):
            Slot.objects.create(teacher=instance)

