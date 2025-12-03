# Інструкції для тестування проєкту в Docker

## Передумови

1. Встановлений Docker та Docker Compose
2. Файл `.env` з необхідними змінними середовища (опціонально)

## Крок 1: Налаштування змінних середовища

Створіть файл `.env` в корені проєкту (якщо його ще немає):

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

## Крок 2: Запуск контейнерів

```bash
# Збудувати та запустити контейнери
docker-compose up --build

# Або в фоновому режимі
docker-compose up -d --build
```

## Крок 3: Створення міграцій та застосування їх

```bash
# Виконати команди в контейнері web
docker-compose exec web python manage.py makemigrations
docker-compose exec web python manage.py migrate
```

## Крок 4: Створення суперкористувача

```bash
docker-compose exec web python manage.py createsuperuser
```

Введіть email та пароль для адміністратора.

## Крок 5: Створення тестових даних

### Через Django shell:

```bash
docker-compose exec web python manage.py shell
```

Потім виконайте:

```python
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
```

### Або через адмін-панель:

1. Відкрийте http://localhost:8000/admin/
2. Увійдіть з обліковими даними суперкористувача
3. Додайте кафедри та наукові інтереси вручну

## Крок 6: Тестування функціоналу

### 6.1. Тестування реєстрації через Microsoft OAuth

1. Відкрийте http://localhost:8000/accounts/login/
2. Натисніть "Увійти через Microsoft"
3. Авторизуйтеся через Microsoft
4. Після авторизації вас перенаправить на сторінку onboarding

### 6.2. Тестування onboarding процесу

1. Виберіть роль (Студент або Викладач)
2. Заповніть необхідні поля:
   - Для студента: група, курс, кафедра (для 3-4 курсу)
   - Для викладача: кафедра, наукові інтереси
3. Натисніть "Зберегти"
4. Вас перенаправить на відповідний профіль

### 6.3. Тестування функціоналу студента

1. Увійдіть як студент
2. Перевірте профіль студента: http://localhost:8000/profiles/student/
3. Натисніть "Обрати викладача"
4. Відфільтруйте викладачів за кафедрою або інтересами
5. Відкрийте профіль викладача
6. Надішліть запит до викладача

### 6.4. Тестування функціоналу викладача

1. Увійдіть як викладач
2. Перевірте профіль викладача: http://localhost:8000/profiles/teacher/
3. Перегляньте слоти: http://localhost:8000/searching/teacher/slots/
4. Створіть новий слот (якщо не досягнуто максимум)
5. Перегляньте запити: http://localhost:8000/searching/teacher/requests/
6. Підтвердіть або відхиліть запит

### 6.5. Тестування повного циклу

1. Створіть два акаунти: один студент, один викладач
2. Студент надсилає запит викладачу
3. Викладач підтверджує запит
4. Перевірте, що студент прикріплений до слота викладача
5. Перевірте статус у профілі студента

## Корисні команди Docker

```bash
# Переглянути логи
docker-compose logs -f web

# Зупинити контейнери
docker-compose down

# Зупинити контейнери та видалити volumes
docker-compose down -v

# Перезапустити контейнери
docker-compose restart

# Виконати команду в контейнері
docker-compose exec web python manage.py <command>

# Відкрити shell в контейнері
docker-compose exec web bash

# Переглянути базу даних
docker-compose exec db psql -U postgres -d kursova_db
```

## Розв'язання проблем

### Проблема: База даних не підключається

```bash
# Перевірте, чи запущений контейнер бази даних
docker-compose ps

# Перевірте логи бази даних
docker-compose logs db

# Перезапустіть контейнери
docker-compose restart
```

### Проблема: Міграції не застосовуються

```bash
# Видаліть старі міграції (якщо потрібно)
docker-compose exec web python manage.py migrate --fake-initial

# Або створіть міграції заново
docker-compose exec web python manage.py makemigrations
docker-compose exec web python manage.py migrate
```

### Проблема: Помилки з Microsoft OAuth

1. Перевірте, чи правильно налаштований `MICROSOFT_TENANT_ID` в `.env`
2. Перевірте налаштування в Azure AD
3. Перевірте, чи правильно налаштований `SITE_ID` в `settings.py`

### Проблема: Статичні файли не завантажуються

```bash
# Зберіть статичні файли
docker-compose exec web python manage.py collectstatic --noinput
```

## Тестування API (якщо буде додано DRF)

```bash
# Переглянути доступні endpoints
curl http://localhost:8000/api/

# Тестувати авторизацію
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password"}'
```

## Очищення та перезапуск

```bash
# Зупинити та видалити контейнери
docker-compose down

# Видалити volumes (видалити базу даних)
docker-compose down -v

# Збудувати та запустити заново
docker-compose up --build -d
```

## Перевірка роботи

1. Відкрийте http://localhost:8000/
2. Перевірте, чи працює авторизація
3. Перевірте, чи працює onboarding
4. Перевірте, чи працює пошук викладачів
5. Перевірте, чи працює створення запитів
6. Перевірте, чи працює підтвердження запитів

## Наступні кроки

1. Додати тести (pytest або Django TestCase)
2. Налаштувати CI/CD
3. Додати логування
4. Налаштувати моніторинг
5. Додати документацію API (якщо використовується DRF)

