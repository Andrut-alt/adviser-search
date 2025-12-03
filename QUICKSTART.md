# Швидкий старт для тестування в Docker

## Крок 1: Запуск контейнерів

```bash
docker-compose up --build
```

## Крок 2: Створення міграцій та застосування

Відкрийте новий термінал і виконайте:

```bash
docker-compose exec web python manage.py makemigrations
docker-compose exec web python manage.py migrate
```

## Крок 3: Створення суперкористувача

```bash
docker-compose exec web python manage.py createsuperuser
```

Введіть:
- Email: `admin@example.com`
- Password: `admin123` (або свій)

## Крок 4: Налаштування Site для django-allauth

```bash
docker-compose exec web python manage.py setup_site
```

## Крок 5: Створення тестових даних

```bash
docker-compose exec web python manage.py init_test_data
```

Це створить:
- Кафедри (6 штук)
- Наукові інтереси (10 штук)

## Крок 6: Доступ до проєкту

1. **Головна сторінка**: http://localhost:8000/
2. **Адмін-панель**: http://localhost:8000/admin/
3. **Вхід через Microsoft**: http://localhost:8000/accounts/login/

## Крок 7: Тестування

### Тестування як студент:

1. Відкрийте http://localhost:8000/accounts/login/
2. Увійдіть через Microsoft OAuth
3. Заповніть onboarding форму (виберіть "Студент")
4. Заповніть: група, курс, кафедра (якщо 3-4 курс)
5. Перейдіть на профіль студента
6. Натисніть "Обрати викладача"
7. Відфільтруйте викладачів
8. Надішліть запит викладачу

### Тестування як викладач:

1. Створіть новий акаунт через Microsoft OAuth
2. Заповніть onboarding форму (виберіть "Викладач")
3. Заповніть: кафедра, наукові інтереси
4. Перейдіть на профіль викладача
5. Перегляньте слоти (мають створитися автоматично - 4 штуки)
6. Перегляньте запити від студентів
7. Підтвердіть або відхиліть запит

## Корисні команди

```bash
# Переглянути логи
docker-compose logs -f web

# Зупинити контейнери
docker-compose down

# Перезапустити
docker-compose restart

# Виконати команду Django
docker-compose exec web python manage.py <command>

# Відкрити shell
docker-compose exec web bash

# Переглянути базу даних
docker-compose exec db psql -U postgres -d kursova_db
```

## Розв'язання проблем

### База даних не підключається

```bash
# Перезапустіть контейнери
docker-compose restart

# Перевірте логи
docker-compose logs db
```

### Міграції не застосовуються

```bash
# Видаліть volumes та перезапустіть
docker-compose down -v
docker-compose up --build
docker-compose exec web python manage.py migrate
```

### Помилки з Microsoft OAuth

Перевірте налаштування в `.env` файлі:
- `MICROSOFT_TENANT_ID`
- `SECRET_KEY`
- `SITE_ID` (в settings.py)

## Структура проєкту

```
adviser-search/
├── mentorion/          # Головні налаштування
├── users/              # Модель користувача
├── profiles/           # Профілі студентів та викладачів
├── searching/          # Пошук та запити
├── docker-compose.yml  # Docker конфігурація
├── Dockerfile          # Образ Django
└── requirements.txt    # Залежності
```

## Наступні кроки

1. Протестуйте весь функціонал
2. Додайте тести (опціонально)
3. Налаштуйте production середовище
4. Додайте документацію API (якщо використовується DRF)

