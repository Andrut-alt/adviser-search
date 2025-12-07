"""Custom user model and manager for email-based authentication."""

from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class UserManager(BaseUserManager):
    """Custom user manager for email-based authentication instead of username."""

    use_in_migrations = True

    def create_user(self, email, password=None, **extra_fields):
        """
        Create and save a regular user with the given email and password.

        Args:
            email (str): User's email address.
            password (str, optional): User's password. If None, sets unusable password.
            **extra_fields: Additional fields for the user model.

        Returns:
            User: The created user instance.

        Raises:
            ValueError: If email is not provided.
        """
        if not email:
            raise ValueError("Email is required")

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)

        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()

        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        """
        Create and save a superuser with the given email and password.

        Args:
            email (str): Superuser's email address.
            password (str): Superuser's password.
            **extra_fields: Additional fields for the user model.

        Returns:
            User: The created superuser instance.
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    """
    Custom user model using email as the primary identifier instead of username.

    Attributes:
        email (EmailField): Unique email address for the user.
    """

    username = None
    email = models.EmailField(unique=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        """Return string representation of the user."""
        return self.email

    @property
    def is_student(self):
        """
        Check if user has a student profile.

        Returns:
            bool: True if user has a StudentProfile, False otherwise.
        """
        from profiles.models import StudentProfile
        return StudentProfile.objects.filter(user=self).exists()

    @property
    def is_teacher(self):
        """
        Check if user has a teacher profile.

        Returns:
            bool: True if user has a TeacherProfile, False otherwise.
        """
        from profiles.models import TeacherProfile
        return TeacherProfile.objects.filter(user=self).exists()

    @property
    def has_profile(self):
        """
        Check if user has any profile (student or teacher).

        Returns:
            bool: True if user has either profile type, False otherwise.
        """
        return self.is_student or self.is_teacher

    @property
    def profile_role(self):
        """
        Get the user's profile role.

        Returns:
            str or None: 'student', 'teacher', or None if no profile exists.
        """
        if self.is_student:
            return 'student'
        if self.is_teacher:
            return 'teacher'
        return None