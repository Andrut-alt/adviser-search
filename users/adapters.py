from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.urls import reverse


class CustomAccountAdapter(DefaultAccountAdapter):
    """Адаптер для налаштування редіректів після логіну"""
    
    def get_login_redirect_url(self, request):
        """Визначає куди редіректити після успішного логіну"""
        return self._get_redirect_url(request)
    
    def _get_redirect_url(self, request):
        """Внутрішня функція для визначення редіректу"""
        # Перевіряємо наявність профілю
        from profiles.models import StudentProfile, TeacherProfile
        
        user = request.user
        if user and user.is_authenticated:
            try:
                # Перевіряємо, чи є профіль студента
                if StudentProfile.objects.filter(user=user).exists():
                    return reverse('profiles:student_profile')
                
                # Перевіряємо, чи є профіль викладача
                if TeacherProfile.objects.filter(user=user).exists():
                    return reverse('profiles:teacher_profile')
            except Exception:
                pass
            
            # Якщо профілю немає, редіректимо на onboarding
            return reverse('profiles:onboarding')
        
        # За замовчуванням редіректимо на головну
        return reverse('home')


class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    """Адаптер для соціальних логінів (Microsoft OAuth)"""
    
    def get_connect_redirect_url(self, request, socialaccount):
        """Редірект після підключення соціального акаунту"""
        adapter = CustomAccountAdapter()
        return adapter._get_redirect_url(request)
    
    def pre_social_login(self, request, sociallogin):
        """Викликається перед соціальним логіном"""
        pass

