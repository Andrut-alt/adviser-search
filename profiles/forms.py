from django import forms
from .models import Profile, Department

class OnboardingForm(forms.Form):
    role = forms.ChoiceField(choices=Profile.Role.choices, label="Ваша роль")
    group = forms.CharField(max_length=50, required=False, label="Група (для студента)")
    department = forms.ModelChoiceField(
        queryset=Department.objects.all(), required=False, label="Кафедра (для викладача)"
    )

    def clean(self):
        cleaned = super().clean()
        role = cleaned.get("role")
        group = cleaned.get("group")
        department = cleaned.get("department")

        if role == Profile.Role.STUDENT and not group:
            self.add_error("group", "Вкажіть групу")
        if role == Profile.Role.TEACHER and not department:
            self.add_error("department", "Оберіть кафедру")
        return cleaned
