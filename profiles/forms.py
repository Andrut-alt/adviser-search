"""Form for user onboarding to create student or teacher profile."""

from django import forms

from .models import Department, ScientificInterest, StudentProfile, TeacherProfile


class OnboardingForm(forms.Form):
    """
    Form for creating student or teacher profile during onboarding.

    Dynamically validates fields based on selected role.
    """

    ROLE_CHOICES = [
        ('student', 'Студент'),
        ('teacher', 'Викладач'),
    ]

    role = forms.ChoiceField(choices=ROLE_CHOICES, label="Ваша роль", widget=forms.RadioSelect)

    group = forms.CharField(max_length=50, required=False, label="Група")
    year_of_study = forms.IntegerField(
        required=False,
        min_value=1,
        max_value=6,
        label="Курс",
        widget=forms.NumberInput(attrs={'min': 1, 'max': 6})
    )
    specialization = forms.CharField(max_length=255, required=False, label="Спеціалізація")
    course_topic = forms.CharField(max_length=500, required=False, label="Тема курсової роботи")
    student_department = forms.ModelChoiceField(
        queryset=Department.objects.all(),
        required=False,
        label="Кафедра (обов'язково для 3-4 курсу)",
        empty_label="Оберіть кафедру"
    )

    teacher_department = forms.ModelChoiceField(
        queryset=Department.objects.all(),
        required=False,
        label="Кафедра",
        empty_label="Оберіть кафедру"
    )
    scientific_interests = forms.ModelMultipleChoiceField(
        queryset=ScientificInterest.objects.all(),
        required=False,
        label="Наукові інтереси",
        widget=forms.CheckboxSelectMultiple
    )
    bio = forms.CharField(
        required=False,
        label="Про себе",
        widget=forms.Textarea(attrs={'rows': 4})
    )

    def clean(self):
        """
        Validate form based on selected role.

        Returns:
            dict: Cleaned form data.

        Raises:
            ValidationError: If required fields are missing for selected role.
        """
        cleaned_data = super().clean()
        role = cleaned_data.get("role")

        if role == 'student':
            self._validate_student_fields(cleaned_data)
        elif role == 'teacher':
            self._validate_teacher_fields(cleaned_data)

        return cleaned_data

    def _validate_student_fields(self, cleaned_data):
        """Validate required fields for student role."""
        if not cleaned_data.get("group"):
            self.add_error("group", "Вкажіть групу")
        
        year_of_study = cleaned_data.get("year_of_study")
        if not year_of_study:
            self.add_error("year_of_study", "Вкажіть курс")
        elif year_of_study in [3, 4] and not cleaned_data.get("student_department"):
            self.add_error("student_department", "Кафедра обов'язкова для студентів 3-4 курсу")

    def _validate_teacher_fields(self, cleaned_data):
        """Validate required fields for teacher role."""
        if not cleaned_data.get("teacher_department"):
            self.add_error("teacher_department", "Оберіть кафедру")

    def save(self, user):
        """
        Create profile based on selected role.

        Args:
            user: User instance to associate with profile.

        Returns:
            StudentProfile or TeacherProfile: Created profile instance.
        """
        cleaned_data = self.cleaned_data
        role = cleaned_data.get("role")

        if role == 'student':
            return self._create_student_profile(user, cleaned_data)
        if role == 'teacher':
            return self._create_teacher_profile(user, cleaned_data)

    def _create_student_profile(self, user, data):
        """Create and return student profile."""
        return StudentProfile.objects.create(
            user=user,
            group=data.get("group"),
            year_of_study=data.get("year_of_study"),
            specialization=data.get("specialization") or None,
            course_topic=data.get("course_topic") or None,
            department=data.get("student_department"),
        )

    def _create_teacher_profile(self, user, data):
        """Create and return teacher profile with scientific interests."""
        profile = TeacherProfile.objects.create(
            user=user,
            department=data.get("teacher_department"),
            bio=data.get("bio") or None,
        )

        scientific_interests = data.get("scientific_interests")
        if scientific_interests:
            profile.scientific_interests.set(scientific_interests)

        return profile
