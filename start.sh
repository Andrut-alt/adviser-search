#!/bin/bash
# Скрипт для швидкого старту проєкту в Docker

echo "🚀 Запуск проєкту..."

# Перевірка, чи запущені контейнери
if [ "$(docker-compose ps -q)" ]; then
    echo "⚠️  Контейнери вже запущені"
    echo "Перезапускаю контейнери..."
    docker-compose down
fi

echo "📦 Збірка та запуск контейнерів..."
docker-compose up --build -d

echo "⏳ Очікування готовності бази даних..."
sleep 10

echo "🔄 Створення міграцій..."
docker-compose exec -T web python manage.py makemigrations

echo "📊 Застосування міграцій..."
docker-compose exec -T web python manage.py migrate

echo "👤 Створення суперкористувача (якщо не існує)..."
docker-compose exec -T web python manage.py shell << EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(email='admin@example.com').exists():
    User.objects.create_superuser('admin@example.com', 'admin123')
    print('✅ Суперкористувач створено: admin@example.com / admin123')
else:
    print('ℹ️  Суперкористувач вже існує')
EOF

echo "🌐 Налаштування Site для django-allauth..."
docker-compose exec -T web python manage.py setup_site

echo "📚 Створення тестових даних..."
docker-compose exec -T web python manage.py init_test_data

echo "✅ Проєкт готовий до тестування!"
echo ""
echo "🌐 Доступні URL:"
echo "   - Головна: http://localhost:8000/"
echo "   - Адмін-панель: http://localhost:8000/admin/"
echo "   - Вхід: http://localhost:8000/accounts/login/"
echo ""
echo "📝 Облікові дані адміністратора:"
echo "   Email: admin@example.com"
echo "   Password: admin123"
echo ""
echo "📋 Корисні команди:"
echo "   - Переглянути логи: docker-compose logs -f web"
echo "   - Зупинити: docker-compose down"
echo "   - Перезапустити: docker-compose restart"

