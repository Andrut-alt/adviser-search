"""Models for consultation slot management and student requests."""

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


class Slot(models.Model):
    """
    Consultation slot for a teacher.

    Each slot can be assigned to one student. Slots are created by teachers
    and requested by students.

    Attributes:
        teacher: ForeignKey to TeacherProfile
        student: OneToOne relationship with StudentProfile (nullable)
        is_available: Whether slot is available for requests
        is_filled: Whether slot is assigned to a student
        created_at: Timestamp of slot creation
        updated_at: Timestamp of last update
    """

    teacher = models.ForeignKey(
        'profiles.TeacherProfile',
        on_delete=models.CASCADE,
        related_name='slots',
        verbose_name="Викладач",
    )
    student = models.OneToOneField(
        'profiles.StudentProfile',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_slot',
        verbose_name="Студент",
    )
    is_available = models.BooleanField(default=True, verbose_name="Доступний")
    is_filled = models.BooleanField(default=False, verbose_name="Зайнятий")
    topic = models.CharField(max_length=500, blank=True, null=True, verbose_name="Тема курсової")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Створено")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Оновлено")

    class Meta:
        verbose_name = "Слот"
        verbose_name_plural = "Слоти"
        ordering = ['-created_at']

    def clean(self):
        """
        Validate and auto-update slot status based on student assignment.

        If student is assigned, mark slot as filled and unavailable.
        """
        if self.student:
            self.is_filled = True
            self.is_available = False
        else:
            self.is_filled = False

    def save(self, *args, **kwargs):
        """Save slot after validation."""
        self.clean()
        super().save(*args, **kwargs)

    def is_full(self):
        """
        Check if slot is occupied.

        Returns:
            bool: True if slot is filled or has assigned student.
        """
        return self.is_filled or self.student is not None

    def __str__(self):
        """Return string representation of slot."""
        if self.student:
            return f"Слот {self.teacher.user.email} - {self.student.user.email}"
        return f"Слот {self.teacher.user.email} - вільний"


class SlotRequest(models.Model):
    """
    Student request for a teacher's consultation slot.

    Attributes:
        student: ForeignKey to StudentProfile
        slot: ForeignKey to Slot
        status: Current status (pending/approved/rejected/cancelled)
        message: Optional message from student
        created_at: Timestamp of request creation
        updated_at: Timestamp of last update
    """

    STATUS_CHOICES = [
        ('pending', 'Очікує'),
        ('approved', 'Підтверджено'),
        ('rejected', 'Відхилено'),
        ('cancelled', 'Скасовано'),
    ]

    student = models.ForeignKey(
        'profiles.StudentProfile',
        on_delete=models.CASCADE,
        related_name='slot_requests',
        verbose_name="Студент",
    )
    slot = models.ForeignKey(
        Slot,
        on_delete=models.CASCADE,
        related_name='requests',
        verbose_name="Слот",
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name="Статус",
    )
    message = models.TextField(blank=True, null=True, verbose_name="Повідомлення")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Створено")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Оновлено")

    class Meta:
        verbose_name = "Запит на слот"
        verbose_name_plural = "Запити на слоти"
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['student', 'slot'],
                condition=models.Q(status='pending'),
                name='unique_pending_request',
            ),
        ]

    def clean(self):
        """
        Validate that student doesn't have duplicate pending requests.

        Raises:
            ValidationError: If student already has pending request for this slot.
        """
        if self.status == 'pending':
            existing = SlotRequest.objects.filter(
                student=self.student,
                slot=self.slot,
                status='pending'
            ).exclude(pk=self.pk)
            if existing.exists():
                raise ValidationError("У вас вже є активний запит на цей слот.")

    def save(self, *args, **kwargs):
        """Save request after validation."""
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        """Return string representation of request."""
        return f"Запит {self.student.user.email} -> {self.slot.teacher.user.email} ({self.get_status_display()})"
