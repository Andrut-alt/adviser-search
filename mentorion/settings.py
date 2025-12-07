from pathlib import Path
import environ


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env(
    DEBUG=(bool, False),
    TIME_ZONE=(str, "Europe/Kyiv"),
    LANGUAGE_CODE=(str, "uk"),
)
environ.Env.read_env(BASE_DIR / ".env")


SECRET_KEY = env("SECRET_KEY")
DEBUG = env("DEBUG")
ALLOWED_HOSTS = [h.strip() for h in env("ALLOWED_HOSTS", default="").split(",") if h.strip()]


DEBUG = True



INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    "users",
    "profiles",
    "searching",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.microsoft",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "allauth.account.middleware.AccountMiddleware",
]

ROOT_URLCONF = "mentorion.urls"

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                
            ],
        },
    },
]
TEMPLATES[0]["DIRS"] = [BASE_DIR / "templates"]

WSGI_APPLICATION = "mentorion.wsgi.application"


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    "default": env.db(
        "DATABASE_URL",
        default="postgres://postgres:Voloshyn02@db:5432/kursova_db"
    )
}

CSRF_TRUSTED_ORIGINS = [
    'https://' + h.strip() for h in env("ALLOWED_HOSTS", default="").split(",") if h.strip() and h.strip() != '*'
]

if env("RENDER_EXTERNAL_HOSTNAME", default=None):
    CSRF_TRUSTED_ORIGINS.append(f'https://{env("RENDER_EXTERNAL_HOSTNAME")}')

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]
AUTH_USER_MODEL = "users.User"

SITE_ID = 1

ACCOUNT_EMAIL_VERIFICATION = "none"
ACCOUNT_AUTHENTICATION_METHOD = "email"
ACCOUNT_EMAIL_REQUIRED = True  # Обов'язково для AUTHENTICATION_METHOD = email
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_USER_MODEL_USERNAME_FIELD = None

# Вимикаємо стандартну реєстрацію - тільки через Microsoft
SOCIALACCOUNT_ONLY = True
SOCIALACCOUNT_AUTO_SIGNUP = True  # Автоматична реєстрація без додаткових форм

# Налаштування редіректів
ACCOUNT_AUTHENTICATED_LOGIN_REDIRECTS = True  # Дозволяємо редірект після логіну
LOGIN_REDIRECT_URL = "/"     # Базовий редірект (буде перевизначено в адаптері)
LOGOUT_REDIRECT_URL = "/"

# Використовуємо кастомний адаптер для редіректів
ACCOUNT_ADAPTER = 'users.adapters.CustomAccountAdapter'
SOCIALACCOUNT_ADAPTER = 'users.adapters.CustomSocialAccountAdapter'

SOCIALACCOUNT_PROVIDERS = {
   "microsoft": {
       
        "APP": {
            "client_id": env("MICROSOFT_CLIENT_ID"),
            "secret": env("MICROSOFT_CLIENT_SECRET"),
            "key": ""
        },
        "TENANT": env("MICROSOFT_TENANT_ID"),
        "SCOPE": ["User.Read"],
        "AUTH_PARAMS": {"access_type": "online"},
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = env("LANGUAGE_CODE")
TIME_ZONE = env("TIME_ZONE")

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = "static/"
STATICFILES_DIRS = ["./static"]  # Вказуємо на d:\adviser-search\static

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
