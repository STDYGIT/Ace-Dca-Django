"""
Django settings for acedca project - Fixed Version
"""
from pathlib import Path
import os
from environ import Env
import dj_database_url

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Environment setup
env = Env()
ENVIRONMENT = os.environ.get('ENVIRONMENT', 'development')

# Load environment-specific .env file
if ENVIRONMENT == 'production':
    env.read_env(os.path.join(BASE_DIR, ".env.production"))
else:
    env.read_env(os.path.join(BASE_DIR, ".env.development"))

# Core settings
SECRET_KEY = env('SECRET_KEY')
DEBUG = (ENVIRONMENT == 'development')

# Site URL configuration
SITE_URL = env('SITE_URL', default='http://127.0.0.1:8000')

ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    '13.60.41.129',
    'acedca.in',
    'www.acedca.in',
]

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'resources',
    'home',
    'tailwind',
    'theme',
    'social_django',
    'minio_storage',
    'django_extensions',
]

# Authentication backends
AUTHENTICATION_BACKENDS = (
    'social_core.backends.google.GoogleOAuth2',
    'django.contrib.auth.backends.ModelBackend',
)

# Google OAuth - Environment specific
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = '922457150888-1nr5d5jvugi4l279gk1ev46dm0no57jp.apps.googleusercontent.com'
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = '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'

if ENVIRONMENT == 'production':
    SOCIAL_AUTH_GOOGLE_OAUTH2_REDIRECT_URI = 'https://13.60.41.129/auth/complete/google-oauth2/'
else:
    SOCIAL_AUTH_GOOGLE_OAUTH2_REDIRECT_URI = 'http://127.0.0.1:8000/auth/complete/google-oauth2/'

LOGIN_URL = '/auth/login/google-oauth2/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

# Tailwind
TAILWIND_APP_NAME = 'theme'
INTERNAL_IPS = ['127.0.0.1']

# Middleware
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'acedca.urls'

# Templates
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'acedca.wsgi.application'

# Database - Environment specific
if ENVIRONMENT == 'production' and env('DATABASE_URL', default=''):
    DATABASES = {
        'default': dj_database_url.parse(env('DATABASE_URL'))
    }
else:
    # Use SQLite for development
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Media files
if ENVIRONMENT == 'production':
    MEDIA_URL = 'https://acedca.in/media/'
    # MinIO configuration for production
    MINIO_STORAGE_ENDPOINT = "127.0.0.1:9000"
    MINIO_STORAGE_ACCESS_KEY = "minioadmin"
    MINIO_STORAGE_SECRET_KEY = "minioadmin"
    MINIO_STORAGE_USE_HTTPS = False
    MINIO_STORAGE_MEDIA_BUCKET_NAME = "media"
    MINIO_STORAGE_AUTO_CREATE_MEDIA_BUCKET = True
    MINIO_STORAGE_MEDIA_URL = "https://acedca.in/media"
    
    STORAGES = {
        "default": {"BACKEND": "minio_storage.storage.MinioMediaStorage"},
        "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
    }
else:
    # Use local media for development
    MEDIA_URL = '/media/'
    MEDIA_ROOT = BASE_DIR / 'media'
    
    STORAGES = {
        "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
        "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
    }

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Email Settings
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = env('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = f'Admin <{EMAIL_HOST_USER}>'

# CORS
CORS_ALLOW_ALL_ORIGINS = DEBUG  # Only allow all origins in development

# Security settings - Environment specific
if ENVIRONMENT == 'production':
    # Production security settings
    SECURE_SSL_REDIRECT = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_BROWSER_XSS_FILTER = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
else:
    # Development - Force HTTP
    SECURE_SSL_REDIRECT = False
    SECURE_HSTS_SECONDS = 0
    SECURE_HSTS_INCLUDE_SUBDOMAINS = False
    SECURE_HSTS_PRELOAD = False
    SECURE_CONTENT_TYPE_NOSNIFF = False
    SECURE_BROWSER_XSS_FILTER = False
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False

SOCIALACCOUNT_LOGIN_ON_GET = True

import mimetypes
mimetypes.add_type("application/javascript", ".js", True)
mimetypes.add_type("text/css", ".css", True)