# Проєкт: Підбір керівника для написання курсової роботи

Веб-додаток на Django для підбору викладача для написання курсової роботи відповідно до кафедри та наукових інтересів.

## Функціонал

### Для студентів:
- Реєстрація через Microsoft OAuth
- Створення профілю студента
- Пошук викладачів за кафедрою та науковими інтересами
- Надсилання запиту викладачу
- Перегляд статусу запиту
- Перегляд інформації про прикріпленого викладача

### Для викладачів:
- Реєстрація через Microsoft OAuth
- Створення профілю викладача
- Керування слотами (створення, видалення)
- Перегляд запитів від студентів
- Підтвердження/відхилення запитів
- Перегляд прикріплених студентів

## Технології

- Django 4.2
- PostgreSQL
- django-allauth (Microsoft OAuth)
- Docker & Docker Compose

## Швидкий старт

### Варіант 1: Використання скрипта (рекомендовано)

```bash
# Надайте права на виконання (Linux/Mac)
chmod +x start.sh

# Запуск
./start.sh
```

### Варіант 2: Ручний запуск

```bash
# 1. Запуск контейнерів
docker-compose up --build -d

# 2. Створення міграцій
docker-compose exec web python manage.py makemigrations

# 3. Застосування міграцій
docker-compose exec web python manage.py migrate

# 4. Створення суперкористувача
docker-compose exec web python manage.py createsuperuser

# 5. Створення тестових даних
docker-compose exec web python manage.py init_test_data
```

## Доступ до проєкту

- **Головна сторінка**: http://localhost:8000/
- **Адмін-панель**: http://localhost:8000/admin/
- **Вхід**: http://localhost:8000/accounts/login/

## Налаштування

### Змінні середовища (.env)

Створіть файл `.env` в корені проєкту:

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
TIME_ZONE=Europe/Kyiv
LANGUAGE_CODE=uk
MICROSOFT_TENANT_ID=your-tenant-id
POSTGRES_DB=kursova_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=Voloshyn02
POSTGRES_HOST=db
POSTGRES_PORT=5432
```

### Налаштування Microsoft OAuth

1. Створіть додаток в Azure AD
2. Додайте redirect URI: `http://localhost:8000/accounts/microsoft/login/callback/`
3. Отримайте Tenant ID та додайте його в `.env`

## Структура проєкту

```
adviser-search/
├── mentorion/              # Головні налаштування Django
├── users/                  # Модель користувача та автентифікація
├── profiles/               # Профілі студентів та викладачів
│   ├── models.py          # StudentProfile, TeacherProfile, Department, ScientificInterest
│   ├── views.py           # Views для профілів
│   ├── forms.py           # OnboardingForm
│   └── management/        # Management commands
├── searching/              # Пошук та запити
│   ├── models.py          # Slot, SlotRequest
│   ├── views.py           # Views для пошуку та запитів
│   └── templates/         # Шаблони
├── docker-compose.yml      # Docker конфігурація
├── Dockerfile              # Образ Django
└── requirements.txt        # Залежності Python
```

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

## Тестування

Детальні інструкції для тестування дивіться в [TESTING.md](TESTING.md) або [QUICKSTART.md](QUICKSTART.md).

## Розв'язання проблем

### База даних не підключається

```bash
docker-compose restart
docker-compose logs db
```

### Міграції не застосовуються

```bash
docker-compose down -v
docker-compose up --build
docker-compose exec web python manage.py migrate
```

### Помилки з Microsoft OAuth

Перевірте налаштування в `.env` файлі та Azure AD.

## Розробка

### Додавання нових моделей

```bash
docker-compose exec web python manage.py makemigrations
docker-compose exec web python manage.py migrate
```

### Створення тестових даних

```bash
docker-compose exec web python manage.py init_test_data
```

## Ліцензія

Цей проєкт є курсовою роботою.

## Автор

Розроблено для курсового проєкту "Підбір керівника для написання курсової роботи".

