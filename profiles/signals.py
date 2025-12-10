# profiles/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import TeacherProfile


@receiver(post_save, sender=TeacherProfile)
def create_slots_for_teacher(sender, instance: TeacherProfile, created: bool, **kwargs):
    """
    automatic adding or removing slots when the teacher's max_slots is changed.
    """
    from searching.models import Slot
    
    current_slots_count = Slot.objects.filter(teacher=instance).count()
    target_slots_count = instance.max_slots
    
    if current_slots_count < target_slots_count:
        slots_to_create = target_slots_count - current_slots_count
        for _ in range(slots_to_create):
            Slot.objects.create(teacher=instance)
    
    elif current_slots_count > target_slots_count:
        slots_to_delete = current_slots_count - target_slots_count
        Slot.objects.filter(teacher=instance, student__isnull=True).order_by('-created_at')[:slots_to_delete].delete()

