"""
Django settings for filemgr project.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.0/ref/settings/
"""
import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ['DJANGO_SECRET_KEY']

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = [
    os.environ['VIRTUAL_HOST'],
    'localhost',
    'userver-filemgr',
]

# Application definition

INSTALLED_APPS = [
    'api',
    'core',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'django_extensions',
    'django_q',
]

MIDDLEWARE = [
    'api.services.cors.cors_middleware_service.CorsMiddlewareService',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'api.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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

WSGI_APPLICATION = 'api.wsgi.application'

# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.environ['POSTGRES_DB'],
        'USER': os.environ['POSTGRES_USER'],
        'PASSWORD': os.environ['POSTGRES_PASS'],
        'HOST': os.environ['POSTGRES_HOST'],
        'PORT': os.environ['POSTGRES_PORT'],
    }
}

# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/

STATIC_URL = '/static/'

STATIC_ROOT = os.path.join(BASE_DIR, 'static')  # noqa: F405

STATICFILES_DIRS = [
    os.path.join (BASE_DIR, 'public'),
]

STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'

APPEND_SLASH = False

AUTH_USER_MODEL = 'core.CustomUser'

# This is NOT a complete production settings file. For more, see:
# See https://docs.djangoproject.com/en/dev/howto/deployment/checklist/

REST_FRAMEWORK = {
    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'core.services.auth.u_server_authentication_service.UServerAuthenticationService',
    ),
    'EXCEPTION_HANDLER': 'api.exceptions.exception_handler.custom_exception_handler',
    'DEFAULT_PAGINATION_CLASS': 'api.pagination.standard_results_set_pagination.StandardResultsSetPagination',
    'PAGE_SIZE': 10,
}

REDIS_HOST = os.getenv('USERVER_REDIS_HOST', 'userver-redis')
REDIS_PORT = int(os.getenv('USERVER_REDIS_PORT', '6379'))
REDIS_DATABASE_DJANGO = int(os.getenv('USERVER_REDIS_DATABASE_DJANGO', '1'))
REDIS_DATABASE_QCLUSTER = int(os.getenv('USERVER_REDIS_DATABASE_QCLUSTER', '2'))

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DATABASE_DJANGO}",
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient'
        },
        'KEY_PREFIX': 'filemgr'
    }
}

SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "default"

Q_CLUSTER = {
    'name': 'uServerFileMgr',
    'workers': 8,
    'recycle': 500,
    'timeout': 60,
    'compress': True,
    'save_limit': 250,
    'queue_limit': 500,
    'cpu_affinity': 1,
    'label': 'uServerFileMgr',
    'redis': {
        'host': REDIS_HOST,
        'port': REDIS_PORT,
        'db': REDIS_DATABASE_QCLUSTER,
    }
}
