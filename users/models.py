from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models

class UserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, email, password=None, **extra_fields):
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
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        return self.create_user(email, password, **extra_fields)

class User(AbstractUser):
    username = None  
    email = models.EmailField(unique=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.email

    @property
    def is_student(self):
        """Перевірка наявності StudentProfile"""
        from profiles.models import StudentProfile
        return StudentProfile.objects.filter(user=self).exists()

    @property
    def is_teacher(self):
        """Перевірка наявності TeacherProfile"""
        from profiles.models import TeacherProfile
        return TeacherProfile.objects.filter(user=self).exists()

    @property
    def has_profile(self):
        """Перевірка наявності будь-якого профілю"""
        return self.is_student or self.is_teacher

    @property
    def profile_role(self):
        """Повертає 'student', 'teacher' або None"""
        if self.is_student:
            return 'student'
        elif self.is_teacher:
            return 'teacher'
        return None