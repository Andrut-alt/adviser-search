"""Custom adapters for Django Allauth authentication and social account handling."""

from allauth.account.adapter import DefaultAccountAdapter
from allauth.account.models import EmailAddress
from allauth.exceptions import ImmediateHttpResponse
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.shortcuts import render
from django.urls import reverse

from profiles.models import StudentProfile, TeacherProfile
from users.models import User


class CustomAccountAdapter(DefaultAccountAdapter):
    """Custom account adapter for handling post-login redirects based on user profile type."""

    def get_login_redirect_url(self, request):
        """
        Determine the redirect URL after successful login.

        Args:
            request: The HTTP request object.

        Returns:
            str: The URL to redirect to after login.
        """
        return self._get_redirect_url(request)

    def _get_redirect_url(self, request):
        """
        Internal method to determine redirect URL based on user profile.

        Args:
            request: The HTTP request object.

        Returns:
            str: The appropriate redirect URL based on user's profile type.
                - Student profile page if user is a student
                - Teacher profile page if user is a teacher
                - Onboarding page if user has no profile
                - Home page if user is not authenticated
        """
        user = request.user

        if not (user and user.is_authenticated):
            return reverse('home')

        try:
            if StudentProfile.objects.filter(user=user).exists():
                return reverse('profiles:student_profile')

            if TeacherProfile.objects.filter(user=user).exists():
                return reverse('profiles:teacher_profile')
        except Exception:
            pass

        return reverse('profiles:onboarding')


class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    """Custom social account adapter for Microsoft OAuth authentication."""

    ALLOWED_EMAIL_DOMAIN = '@lnu.edu.ua'

    def get_connect_redirect_url(self, request, socialaccount):
        """
        Determine redirect URL after social account connection.

        Args:
            request: The HTTP request object.
            socialaccount: The social account being connected.

        Returns:
            str: The redirect URL.
        """
        adapter = CustomAccountAdapter()
        return adapter._get_redirect_url(request)

    def pre_social_login(self, request, sociallogin):
        """
        Handle pre-login logic for social authentication.

        This method:
        1. Validates email domain (@lnu.edu.ua only)
        2. Links existing user accounts with Microsoft OAuth
        3. Creates EmailAddress records for proper account management

        Args:
            request: The HTTP request object.
            sociallogin: The social login instance.

        Raises:
            ImmediateHttpResponse: If email domain is not allowed.
        """
        if sociallogin.is_existing:
            return

        email = sociallogin.account.extra_data.get('email')
        if not email:
            return

        if not email.lower().endswith(self.ALLOWED_EMAIL_DOMAIN):
            response = render(request, 'socialaccount/authentication_error.html', {
                'error': f'Only email addresses with domain {self.ALLOWED_EMAIL_DOMAIN} are allowed. Your email: {email}'
            })
            raise ImmediateHttpResponse(response)

        try:
            user = User.objects.get(email__iexact=email)
            sociallogin.user = user
            sociallogin.save(request)

            EmailAddress.objects.get_or_create(
                user=user,
                email=email.lower(),
                defaults={'verified': True, 'primary': True}
            )
        except User.DoesNotExist:
            pass
