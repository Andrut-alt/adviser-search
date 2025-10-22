from django.shortcuts import render

from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import FormView
from django.urls import reverse_lazy
from .forms import OnboardingForm


@method_decorator(login_required, name="dispatch")
class OnboardingView(FormView):
    template_name = "profiles/onboarding.html"
    form_class = OnboardingForm
    success_url = reverse_lazy("onboarding")  # або на дашборд

    def get_form_kwargs(self):
        kw = super().get_form_kwargs()
        kw["user"] = self.request.user
        kw["instance"] = getattr(self.request.user, "profile", None)
        return kw

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)

