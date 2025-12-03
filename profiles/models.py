# profiles/models.py
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


class Department(models.Model):
    name = models.CharField(max_length=255, unique=True)

    class Meta:
        verbose_name = "Кафедра"
        verbose_name_plural = "Кафедри"

    def __str__(self):
        return self.name


class ScientificInterest(models.Model):
    name = models.CharField(max_length=255, unique=True, verbose_name="Назва")
    description = models.TextField(blank=True, null=True, verbose_name="Опис")

    class Meta:
        verbose_name = "Науковий інтерес"
        verbose_name_plural = "Наукові інтереси"

    def __str__(self):
        return self.name


class StudentProfile(models.Model):
    YEAR_CHOICES = [
        (1, '1 курс'),
        (2, '2 курс'),
        (3, '3 курс'),
        (4, '4 курс'),
 
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="student_profile",
    )
    group = models.CharField(max_length=50, verbose_name="Група")
    year_of_study = models.IntegerField(choices=YEAR_CHOICES, verbose_name="Курс")
    specialization = models.CharField(max_length=255, blank=True, null=True, verbose_name="Спеціалізація")
    course_topic = models.CharField(max_length=500, blank=True, null=True, verbose_name="Тема курсової роботи")
    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="students",
        verbose_name="Кафедра",
    )

    def clean(self):
        """Валідація: кафедра обов'язкова для 3-4 курсу"""
        if self.year_of_study in [3, 4] and not self.department:
            raise ValidationError({"department": "Кафедра обов'язкова для студентів 3-4 курсу."})

    def can_change_topic(self):
        """Перевірка, чи можна змінити тему (тільки до підтвердження викладача)"""
        # Перевіримо, чи є підтверджений запит на слот
        if hasattr(self, 'assigned_slot') and self.assigned_slot:
            return False  # Якщо є прикріплений слот, тему змінити не можна
        # Перевіримо, чи є підтверджений запит
        approved_requests = self.slot_requests.filter(status='approved')
        if approved_requests.exists():
            return False
        return True

    def __str__(self):
        return f"{self.user.email} (Студент, {self.get_year_of_study_display()})"


class TeacherProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="teacher_profile",
    )
    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        blank=False,
        related_name="teachers",
        verbose_name="Кафедра",
    )
    scientific_interests = models.ManyToManyField(
        ScientificInterest,
        blank=True,
        related_name="teachers",
        verbose_name="Наукові інтереси",
    )
    bio = models.TextField(blank=True, null=True, verbose_name="Про себе")
    max_slots = models.IntegerField(default=4, verbose_name="Максимальна кількість слотів")

    def available_slots_count(self):
        """Кількість вільних слотів"""
        return self.slots.filter(is_available=True, is_filled=False).count()

    def total_slots_count(self):
        """Загальна кількість слотів"""
        return self.slots.count()

    def filled_slots_count(self):
        """Кількість зайнятих слотів"""
        return self.slots.filter(is_filled=True).count()

    def __str__(self):
        return f"{self.user.email} (Викладач)"


# Стара модель Profile залишається для зворотної сумісності під час міграції
# Буде видалена після міграції даних
class Profile(models.Model):
    class Role(models.TextChoices):
        STUDENT = "student", "Студент"
        TEACHER = "teacher", "Викладач"

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
    )
    role = models.CharField(max_length=20, choices=Role.choices)

    # Поля для студента:
    group = models.CharField(max_length=50, blank=True)

    # Поля для викладача:
    department = models.ForeignKey(
        Department, on_delete=models.SET_NULL, null=True, blank=True, related_name="profiles"
    )

    # На майбутнє: інтереси, курс, тема тощо

    def clean(self):
        # Вимоги залежно від ролі
        if self.role == self.Role.STUDENT:
            if not self.group:
                raise ValidationError({"group": "Група обов'язкова для студента."})
            # для студента кафедра не обов'язкова
        elif self.role == self.Role.TEACHER:
            if not self.department:
                raise ValidationError({"department": "Кафедра обов'язкова для викладача."})

    def __str__(self):
        return f"{self.user.email} ({self.get_role_display()})"
