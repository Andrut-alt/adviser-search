from django import forms
from .models import Department, ScientificInterest, StudentProfile, TeacherProfile


class OnboardingForm(forms.Form):
    ROLE_CHOICES = [
        ('student', 'Студент'),
        ('teacher', 'Викладач'),
    ]

    role = forms.ChoiceField(choices=ROLE_CHOICES, label="Ваша роль", widget=forms.RadioSelect)

    # Поля для студента
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

    # Поля для викладача
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
        cleaned_data = super().clean()
        role = cleaned_data.get("role")
        group = cleaned_data.get("group")
        year_of_study = cleaned_data.get("year_of_study")
        student_department = cleaned_data.get("student_department")
        teacher_department = cleaned_data.get("teacher_department")

        if role == 'student':
            if not group:
                self.add_error("group", "Вкажіть групу")
            if not year_of_study:
                self.add_error("year_of_study", "Вкажіть курс")
            elif year_of_study in [3, 4] and not student_department:
                self.add_error("student_department", "Кафедра обов'язкова для студентів 3-4 курсу")

        elif role == 'teacher':
            if not teacher_department:
                self.add_error("teacher_department", "Оберіть кафедру")

        return cleaned_data

    def save(self, user):
        """Створює профіль відповідно до вибраної ролі"""
        cleaned_data = self.cleaned_data
        role = cleaned_data.get("role")

        if role == 'student':
            profile = StudentProfile.objects.create(
                user=user,
                group=cleaned_data.get("group"),
                year_of_study=cleaned_data.get("year_of_study"),
                specialization=cleaned_data.get("specialization") or None,
                course_topic=cleaned_data.get("course_topic") or None,
                department=cleaned_data.get("student_department"),
            )
        elif role == 'teacher':
            profile = TeacherProfile.objects.create(
                user=user,
                department=cleaned_data.get("teacher_department"),
                bio=cleaned_data.get("bio") or None,
            )
            # Додаємо наукові інтереси
            scientific_interests = cleaned_data.get("scientific_interests")
            if scientific_interests:
                profile.scientific_interests.set(scientific_interests)

        return profile
