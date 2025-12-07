"""Profile models for students and teachers."""

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


class Department(models.Model):
    """University department model."""

    name = models.CharField(max_length=255, unique=True)

    class Meta:
        verbose_name = "Кафедра"
        verbose_name_plural = "Кафедри"

    def __str__(self):
        """Return department name."""
        return self.name


class ScientificInterest(models.Model):
    """Scientific research interest or topic."""

    name = models.CharField(max_length=255, unique=True, verbose_name="Назва")
    description = models.TextField(blank=True, null=True, verbose_name="Опис")

    class Meta:
        verbose_name = "Науковий інтерес"
        verbose_name_plural = "Наукові інтереси"

    def __str__(self):
        """Return interest name."""
        return self.name


class StudentProfile(models.Model):
    """
    Student profile with academic information.

    Attributes:
        user: One-to-one relationship with User model
        group: Student's group identifier
        year_of_study: Current year (1-4)
        specialization: Optional specialization field
        course_topic: Course work topic
        department: Required for 3rd and 4th year students
    """

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
        """
        Validate that department is set for 3rd and 4th year students.

        Raises:
            ValidationError: If department is missing for 3rd or 4th year student.
        """
        if self.year_of_study in [3, 4] and not self.department:
            raise ValidationError({"department": "Кафедра обов'язкова для студентів 3-4 курсу."})

    def can_change_topic(self):
        """
        Check if student can change their course topic.

        Topic can only be changed before teacher approval.

        Returns:
            bool: True if topic can be changed, False otherwise.
        """
        if hasattr(self, 'assigned_slot') and self.assigned_slot:
            return False

        approved_requests = self.slot_requests.filter(status='approved')
        return not approved_requests.exists()

    def __str__(self):
        """Return string representation of student profile."""
        return f"{self.user.email} (Студент, {self.get_year_of_study_display()})"


class TeacherProfile(models.Model):
    """
    Teacher profile with academic and administrative information.

    Attributes:
        user: One-to-one relationship with User model
        department: Teacher's department
        scientific_interests: Many-to-many relationship with research interests
        bio: Optional biography text
        max_slots: Maximum number of consultation slots
        is_approved: Admin approval status
        approved_by: User who approved the teacher
        approved_at: Timestamp of approval
    """

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

    is_approved = models.BooleanField(default=False, verbose_name="Підтверджено")
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approved_teachers",
        verbose_name="Підтверджено користувачем"
    )
    approved_at = models.DateTimeField(null=True, blank=True, verbose_name="Дата підтвердження")

    def available_slots_count(self):
        """
        Get count of available consultation slots.

        Returns:
            int: Number of available and unfilled slots.
        """
        return self.slots.filter(is_available=True, is_filled=False).count()

    def total_slots_count(self):
        """
        Get total count of all slots.

        Returns:
            int: Total number of slots.
        """
        return self.slots.count()

    def filled_slots_count(self):
        """
        Get count of filled slots.

        Returns:
            int: Number of filled slots.
        """
        return self.slots.filter(is_filled=True).count()

    def __str__(self):
        """Return string representation of teacher profile."""
        return f"{self.user.email} (Викладач)"


class Profile(models.Model):
    """
    Legacy profile model for backward compatibility during migration.

    DEPRECATED: Will be removed after data migration is complete.
    Use StudentProfile or TeacherProfile instead.
    """

    class Role(models.TextChoices):
        STUDENT = "student", "Студент"
        TEACHER = "teacher", "Викладач"

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
    )
    role = models.CharField(max_length=20, choices=Role.choices)
    group = models.CharField(max_length=50, blank=True)
    department = models.ForeignKey(
        Department, on_delete=models.SET_NULL, null=True, blank=True, related_name="profiles"
    )

    def clean(self):
        """
        Validate role-specific requirements.

        Raises:
            ValidationError: If required fields are missing for the role.
        """
        if self.role == self.Role.STUDENT and not self.group:
            raise ValidationError({"group": "Група обов'язкова для студента."})

        if self.role == self.Role.TEACHER and not self.department:
            raise ValidationError({"department": "Кафедра обов'язкова для викладача."})

    def __str__(self):
        """Return string representation of profile."""
        return f"{self.user.email} ({self.get_role_display()})"
