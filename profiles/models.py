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
