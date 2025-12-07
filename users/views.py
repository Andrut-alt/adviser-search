from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.http import HttpResponse
from users.models import User

# Create your views here.

def dev_login(request):
    """Тимчасовий вхід для розробки - ВИДАЛИТИ В ПРОДАКШЕНІ!"""
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            return redirect('home')
        except User.DoesNotExist:
            return HttpResponse('Користувача не знайдено')
    
    # Показуємо список користувачів
    users = User.objects.all()
    html = '''
    <html>
    <head><title>Dev Login</title></head>
    <body style="font-family: Arial; padding: 2rem;">
        <h1>🔧 Development Login</h1>
        <p style="color: red;"><strong>ТІЛЬКИ ДЛЯ РОЗРОБКИ!</strong></p>
        <form method="post">
    '''
    
    # CSRF token
    from django.middleware.csrf import get_token
    html += f'<input type="hidden" name="csrfmiddlewaretoken" value="{get_token(request)}">'
    
    html += '<select name="email" style="padding: 0.5rem; font-size: 1rem;">'
    
    for user in users:
        role = 'Викладач' if user.is_teacher else ('Студент' if user.is_student else 'Без профілю')
        html += f'<option value="{user.email}">{user.email} ({role})</option>'
    
    html += '''
            </select>
            <button type="submit" style="padding: 0.5rem 1rem; margin-left: 1rem;">Увійти</button>
        </form>
    </body>
    </html>
    '''
    return HttpResponse(html)
