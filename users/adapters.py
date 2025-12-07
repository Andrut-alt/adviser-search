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
        """Автоматично зв'язуємо існуючий акаунт з Microsoft OAuth"""
        # Якщо це вже зв'язаний social account, пропускаємо
        if sociallogin.is_existing:
            return
        
        # Отримуємо email з Microsoft
        email = sociallogin.account.extra_data.get('email')
        if not email:
            return
        
        # Перевіряємо домен email
        if not email.lower().endswith('@lnu.edu.ua'):
            from allauth.exceptions import ImmediateHttpResponse
            from django.shortcuts import render
            
            response = render(request, 'socialaccount/authentication_error.html', {
                'error': f'Дозволені тільки email адреси з доменом @lnu.edu.ua. Ваш email: {email}'
            })
            raise ImmediateHttpResponse(response)
        
        # Шукаємо користувача з таким email
        from users.models import User
        from allauth.account.models import EmailAddress
        
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
