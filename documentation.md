# ДОДАТОК А: Розширена документація проекту "Підбір керівника для написання курсової роботи"

## 1. Розширена інструкція запуску проекту

### Передумови
- Docker та Docker Compose встановлені на системі
- Git для клонування репозиторію (якщо потрібно)
- Веб-браузер для доступу до додатку

### Крок 1: Клонування та підготовка проекту
```bash
# Клонувати репозиторій (якщо не клонований)
git clone <repository-url>
cd adviser-search

# Надати права на виконання скрипту запуску (Linux/Mac)
chmod +x start.sh
```

### Крок 2: Налаштування змінних середовища
Створіть файл `.env` у кореневій папці проекту з наступним вмістом:

```env
# Django налаштування
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# База даних PostgreSQL
POSTGRES_DB=kursova_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your-password
DATABASE_URL=postgresql://postgres:your-password@db:5432/kursova_db

# Microsoft OAuth налаштування
SOCIAL_AUTH_MICROSOFT_CLIENT_ID=your-client-id
SOCIAL_AUTH_MICROSOFT_CLIENT_SECRET=your-client-secret
SOCIAL_AUTH_MICROSOFT_TENANT_ID=your-tenant-id

# Часовий пояс та мова
TIME_ZONE=Europe/Kyiv
LANGUAGE_CODE=uk
```

### Крок 3: Запуск через скрипт (рекомендовано)
```bash
./start.sh
```
Цей скрипт автоматично:
- Збирає Docker образи
- Запускає контейнери
- Застосовує міграції бази даних
- Створює суперкористувача
- Збирає статичні файли

### Крок 4: Альтернативний ручний запуск
Якщо скрипт не працює, виконайте наступні команди:

```bash
# 1. Збірка та запуск контейнерів
docker-compose up --build -d

# 2. Зачекати, поки база даних запуститься (30-60 секунд)
sleep 30

# 3. Створення міграцій
docker-compose exec web python manage.py makemigrations

# 4. Застосування міграцій
docker-compose exec web python manage.py migrate

# 5. Створення суперкористувача
docker-compose exec web python manage.py createsuperuser

# 6. Збірка статичних файлів
docker-compose exec web python manage.py collectstatic --noinput
```

### Крок 5: Налаштування Microsoft OAuth (опціонально для повного функціонування)
1. Перейдіть до [Azure Active Directory](https://portal.azure.com/#blade/Microsoft_AAD_IAM/ActiveDirectoryMenuBlade/Overview)
2. Створіть новий додаток у "App registrations"
3. Додайте redirect URI: `http://localhost:8000/accounts/microsoft/login/callback/`
4. Скопіюйте Client ID, Client Secret та Tenant ID у файл `.env`

### Крок 6: Доступ до додатку
- **Головна сторінка**: http://localhost:8000/
- **Адмін-панель**: http://localhost:8000/admin/
- **Вхід через Microsoft**: http://localhost:8000/accounts/microsoft/login/

### Крок 7: Створення тестових даних (опціонально)
```bash
# Запуск команди для створення початкових даних
docker-compose exec web python manage.py setup_site
```

### Зупинка проекту
```bash
docker-compose down
```

### Перезапуск після змін у коді
```bash
docker-compose restart web
```

### Перегляд логів
```bash
# Логи веб-додатку
docker-compose logs -f web

# Логи бази даних
docker-compose logs -f db
```

### Вирішення проблем
- **Порт 8000 зайнятий**: Змініть порт у `docker-compose.yml`
- **Помилки міграцій**: `docker-compose down -v` та повторний запуск
- **Проблеми з OAuth**: Перевірте налаштування у Azure AD та `.env`

## 2. Опис файлів проекту

### Коренева структура проекту

#### adviser-search/
Коренева папка проекту, містить конфігураційні файли та скрипти запуску.

- **README.md**: Основна документація проекту з описом функціоналу та базовими інструкціями запуску
- **requirements.txt**: Список Python залежностей для проекту
- **docker-compose.yml**: Конфігурація Docker Compose для оркестрації контейнерів
- **Dockerfile**: Інструкції для збірки Docker образу веб-додатку
- **start.sh**: Скрипт автоматичного запуску проекту
- **create_superuser.py**: Скрипт для створення суперкористувача Django
- **manage.py**: Стандартний Django management скрипт

### mentorion/
Головний Django додаток з налаштуваннями проекту.

- **__init__.py**: Позначає папку як Python пакет
- **settings.py**: Основні налаштування Django (бази даних, додатки, middleware, OAuth тощо)
- **urls.py**: Головний URL конфігуратор проекту
- **wsgi.py**: WSGI конфігурація для розгортання
- **asgi.py**: ASGI конфігурація для асинхронних додатків

### users/
Додаток для управління користувачами та автентифікацією.

- **__init__.py**: Python пакет
- **models.py**: Розширення стандартної моделі User Django
- **admin.py**: Реєстрація моделей в адмін-панелі
- **apps.py**: Конфігурація додатку
- **adapters.py**: Адаптери для django-allauth
- **signals.py**: Сигнали Django для автоматизації процесів
- **tests.py**: Unit тести для додатку
- **management/commands/setup_site.py**: Management команда для ініціалізації сайту

### profiles/
Додаток для управління профілями студентів та викладачів.

- **__init__.py**: Python пакет
- **models.py**: Моделі Department, ScientificInterest, StudentProfile, TeacherProfile
- **views.py**: Представлення для створення та редагування профілів
- **forms.py**: Django форми для онбордингу та профілів
- **admin.py**: Адмін інтерфейс для моделей профілів
- **apps.py**: Конфігурація додатку
- **decorators.py**: Декоратори для перевірки ролей користувачів
- **signals.py**: Сигнали для автоматизації створення профілів
- **tests.py**: Тести для функціоналу профілів
- **urls.py**: URL патерни для профілів

#### profiles/templates/profiles/
HTML шаблони для профілів.

- **onboarding.html**: Шаблон для первинного заповнення профілю
- **student_profile.html**: Шаблон профілю студента
- **teacher_profile.html**: Шаблон профілю викладача

#### profiles/migrations/
Міграції бази даних для моделей профілів.

- **0001_initial.py**: Початкова міграція
- **0002_initial.py**: Друга початкова міграція
- **0003_scientificinterest_teacherprofile_studentprofile.py**: Додавання наукових інтересів та профілів
- **0004_teacherprofile_approved_at_and_more.py**: Додавання полів підтвердження та дати

### searching/
Додаток для системи пошуку та призначення слотів.

- **__init__.py**: Python пакет
- **models.py**: Моделі Slot та SlotRequest
- **views.py**: Представлення для пошуку, створення слотів та управління запитами
- **admin.py**: Адмін інтерфейс для слотів та запитів
- **apps.py**: Конфігурація додатку
- **tests.py**: Тести для пошуку та слотів
- **urls.py**: URL патерни для пошуку

#### searching/templates/searching/
HTML шаблони для пошуку та слотів.

- **edit_slot.html**: Шаблон редагування слоту
- **filter_teachers.html**: Шаблон фільтрації викладачів
- **slot_detail.html**: Детальний перегляд слоту
- **teacher_detail.html**: Детальний перегляд профілю викладача
- **teacher_requests.html**: Шаблон запитів викладача
- **teacher_slots.html**: Шаблон слотів викладача

#### searching/migrations/
Міграції для моделей пошуку.

- **0001_initial.py**: Початкова міграція слотів
- **0002_slot_topic.py**: Додавання поля теми до слоту

### static/
Статичні файли проекту.

#### static/css/
CSS стилі.

- **academic-minimalism.css**: Основні стилі додатку з академічним дизайном

### users/templates/
Шаблони для користувачів та автентифікації.

#### users/templates/base.html
Базовий HTML шаблон з навігацією та структурою сторінки.

#### users/templates/account/
Шаблони для django-allauth.

- **login.html**: Сторінка входу
- **logout.html**: Сторінка виходу
- **signup.html**: Сторінка реєстрації

#### users/templates/socialaccount/
Шаблони для соціальної автентифікації.

- **authentication_error.html**: Помилка автентифікації
- **login.html**: Вхід через соціальні мережі
- **signup.html**: Реєстрація через соціальні мережі

### profiles/models.py
Містить моделі для профілів користувачів:

- **Department**: Модель кафедри університету з унікальною назвою
- **ScientificInterest**: Наукові інтереси та теми досліджень
- **StudentProfile**: Профіль студента з групою, курсом, спеціалізацією, темою курсової та кафедрою (обов'язкова для 3-4 курсів)
- **TeacherProfile**: Профіль викладача з кафедрою, інтересами, біографією, максимальними слотами та статусом підтвердження

Ключові методи:
- `StudentProfile.clean()`: Валідація обов'язкової кафедри для старших курсів
- `StudentProfile.can_change_topic()`: Перевірка можливості зміни теми після призначення викладача

### searching/models.py
Моделі для системи слотів та запитів:

- **Slot**: Консультаційний слот викладача з інформацією про доступність, студента, тему
- **SlotRequest**: Запит студента на слот зі статусом (pending/approved/rejected/cancelled)

Ключові методи:
- `Slot.clean()`: Автоматичне оновлення статусу при призначенні студента
- `Slot.is_full()`: Перевірка зайнятості слоту

### profiles/views.py
Представлення для управління профілями:

- `onboarding_view()`: Онбординг нових користувачів
- `student_profile_view()`: Перегляд/редагування профілю студента
- `teacher_profile_view()`: Перегляд/редагування профілю викладача

### searching/views.py
Представлення для пошуку та слотів:

- `filter_teachers()`: Фільтрація викладачів за критеріями
- `teacher_detail()`: Детальний перегляд викладача та його слотів
- `create_slot()`: Створення нового слоту викладачем
- `edit_slot()`: Редагування існуючого слоту
- `request_slot()`: Подання запиту на слот
- `manage_requests()`: Управління запитами викладачем

### profiles/forms.py
Django форми:

- **OnboardingForm**: Форма для первинного вибору ролі (студент/викладач)
- **StudentProfileForm**: Форма профілю студента
- **TeacherProfileForm**: Форма профілю викладача

### users/models.py
Розширення стандартної моделі User Django з додатковими полями та методами.

### users/adapters.py
Адаптери для django-allauth для кастомізації процесу автентифікації через Microsoft OAuth.

### profiles/signals.py
Сигнали Django для автоматичного створення профілів після реєстрації користувачів.

### profiles/decorators.py
Декоратори для перевірки ролей користувачів (студент/викладач) перед доступом до view.

### users/management/commands/setup_site.py
Management команда Django для ініціалізації сайту тестовими даними (кафедри, інтереси тощо).

### docker-compose.yml
Конфігурація Docker Compose з сервісами:
- **web**: Django додаток на Gunicorn
- **db**: PostgreSQL база даних
- **redis**: (якщо використовується) для кешування

### Dockerfile
Інструкції збірки Docker образу:
- Базується на Python 3.11
- Встановлює залежності з requirements.txt
- Копіює код проекту
- Налаштовує статичні файли

### requirements.txt
Python залежності:
- Django==4.2
- django-allauth[socialaccount]
- psycopg2-binary
- gunicorn
- whitenoise
- python-environ

### start.sh
Bash скрипт для автоматичного запуску проекту з перевірками та логуванням.

### Backend
- **Django 4.2**: Веб-фреймворк
- **PostgreSQL**: База даних
- **django-allauth**: Автентифікація через Microsoft OAuth
- **Docker**: Контейнеризація
- **Gunicorn**: WSGI сервер
- **Whitenoise**: Обслуговування статичних файлів

### Frontend
- **Django Templates**: Шаблонізація
- **CSS**: Стилізація
- **HTML5**: Розмітка

### DevOps
- **Docker Compose**: Оркестрація
- **Git**: Версійний контроль

## 4. Безпека та продуктивність

### Безпека
- CSRF захист
- SQL injection захист через ORM
- XSS захист через шаблони
- HTTPS рекомендовано для продакшену
- Секрети у змінних середовища

### Продуктивність
- Docker контейнеризація
- PostgreSQL для складних запитів
- Статичні файли через Whitenoise
- Оптимізація запитів через select_related/prefetch_related

## 5. Майбутній розвиток

Проект має потенціал для розширення:
- Інтеграція з календарями
- Система повідомлень
- Рейтингова система
- Мобільний додаток
- API документація
- Тестування та CI/CD

---

*Цей документ є частиною курсової роботи "Підбір керівника для написання курсової роботи".*</content>
<parameter name="filePath">d:\adviser-search\adviser-search\documentation.md