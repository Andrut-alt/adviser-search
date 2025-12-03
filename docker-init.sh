#!/bin/bash
# Скрипт для ініціалізації проєкту в Docker

echo "Очікування підключення до бази даних..."
sleep 5

echo "Виконую міграції..."
python manage.py makemigrations
python manage.py migrate

echo "Створюю суперкористувача (якщо не існує)..."
python manage.py shell << EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(email='admin@example.com').exists():
    User.objects.create_superuser('admin@example.com', 'admin123')
    print('Суперкористувач створено: admin@example.com / admin123')
else:
    print('Суперкористувач вже існує')
EOF

echo "Створюю тестові дані..."
python manage.py shell << EOF
from profiles.models import Department, ScientificInterest

# Створюємо кафедри
departments = [
    'Кафедра інформаційних систем',
    'Кафедра комп\'ютерних наук',
    'Кафедра програмної інженерії',
    'Кафедра математики',
]

for dept_name in departments:
    Department.objects.get_or_create(name=dept_name)

# Створюємо наукові інтереси
interests = [
    'Машинне навчання',
    'Веб-розробка',
    'Бази даних',
    'Кібербезпека',
    'Мобільні додатки',
    'Штучний інтелект',
]

for interest_name in interests:
    ScientificInterest.objects.get_or_create(name=interest_name)

print('Тестові дані створено')
EOF

echo "Готово! Проєкт готовий до тестування."

