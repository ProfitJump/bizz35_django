# Import/lode all files and packages needed to run the setting file.
import os
import sys
import dj_database_url
from pathlib import Path
from django.contrib import staticfiles
from django.contrib.messages import constants as messages
from django.core.management.utils import get_random_secret_key
from dotenv import load_dotenv

load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: Keep the secret key used in production secret!
# SECURITY WARNING: Don't run with debug turned on in production!
DEBUG = os.getenv("DEBUG", "False") == "True"
DEVELOPMENT_MODE = os.getenv("DEVELOPMENT_MODE", "False") == "True"
SECRET_KEY = os.getenv("SECRET_KEY", get_random_secret_key())
USE_SPACES = os.getenv('USE_SPACES') == 'True'
SITE_ID = 1
if DEVELOPMENT_MODE is True:
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False
    SECURE_SSL_REDIRECT = False
else:
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_SSL_REDIRECT = True
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

ALLOWED_HOSTS = [
    '*',
]

# Redirect to home URL after login (Default redirects to /accounts/profile/)
AUTH_USER_MODEL = 'authentication.User'
LOGIN_URL = 'auth.login'
LOGIN_REDIRECT_URL = '/dashboard/profile'
LOGOUT_REDIRECT_URL = '/'

# Application definition

INSTALLED_APPS = [
    "whitenoise.runserver_nostatic",
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'storages',
    'hijack',
    'hijack.contrib.admin',

    # Custom Applications
    'authentication',
    'dashboard',
    'frontend',
    'stripe_api',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    "whitenoise.middleware.WhiteNoiseMiddleware",
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'hijack.middleware.HijackUserMiddleware',
]

ROOT_URLCONF = 'mainapp.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'mainapp.wsgi.application'

# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases


if DEVELOPMENT_MODE is True:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.getenv('db_name'),
            'USER': os.getenv('db_user'),
            'PASSWORD': os.getenv('db_pass'),
            'HOST': os.getenv('db_host'),
            'PORT': os.getenv('db_port')
        }
    }
elif len(sys.argv) > 0 and sys.argv[1] != 'collectstatic':
    if os.getenv("DATABASE_URL", None) is None:
        raise Exception("DATABASE_URL environment variable not defined")
    DATABASES = {
        'default': dj_database_url.config(
            default=os.getenv('DATABASE_URL'),
            conn_max_age=600,
            conn_health_checks=True,
        )
    }

# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME':
            'django.contrib.auth.password_validation.'
            'UserAttributeSimilarityValidator',
    },
    {
        'NAME':
            'django.contrib.auth.password_validation.'
            'MinimumLengthValidator',
    },
    {
        'NAME':
            'django.contrib.auth.password_validation.'
            'CommonPasswordValidator',
    },
    {
        'NAME':
            'django.contrib.auth.password_validation.'
            'NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'America/Denver'

USE_I18N = True
USE_L10N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'mainapp/staticfiles')
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'frontend/templates/static'),
    os.path.join(BASE_DIR, 'stripe_api/templates/static'),
    os.path.join(BASE_DIR, 'dashboard/templates/static'),
)

if USE_SPACES is True:
    AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
    AWS_STORAGE_BUCKET_NAME = os.getenv('AWS_STORAGE_BUCKET_NAME')
    AWS_DEFAULT_ACL = 'public-read'
    AWS_S3_ENDPOINT_URL = 'https://data1.profitjump.network'
    AWS_S3_OBJECT_PARAMETERS = {
        'CacheControl': 'max-age=86400'
    }
    AWS_MEDIA_LOCATION = 'public_media'
    PUBLIC_MEDIA_LOCATION = 'public_media'
    MEDIA_URL = f'https://{AWS_STORAGE_BUCKET_NAME}.{AWS_S3_ENDPOINT_URL}/{PUBLIC_MEDIA_LOCATION}/'
    DEFAULT_FILE_STORAGE = 'mainapp.storage_backends.MediaStorage'
else:
    MEDIA_ROOT = os.path.join(BASE_DIR, 'mainapp/staticfiles/media')
    MEDIA_URL = '/media/'

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

MESSAGE_TAGS = {
    messages.DEBUG: 'alert-secondary',
    messages.INFO: 'alert-info',
    messages.SUCCESS: 'alert-success',
    messages.WARNING: 'alert-warning',
    messages.ERROR: 'alert-danger',
}

STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY_TEST") if DEVELOPMENT_MODE is True else os.getenv("STRIPE_SECRET_KEY")
STRIPE_PUB_KEY = os.getenv("STRIPE_PUB_KEY_TEST") if DEVELOPMENT_MODE is True else os.getenv("STRIPE_PUB_KEY")
STRIPE_ENDPOINT_SECRET = os.getenv("STRIPE_ENDPOINT_SECRET_TEST") if DEVELOPMENT_MODE is True else os.getenv("STRIPE_ENDPOINT_SECRET")
STRIPE_CONNECT_CLIENT_ID = os.getenv("STRIPE_CONNECT_CLIENT_ID_TEST") if DEVELOPMENT_MODE is True else os.getenv("STRIPE_CONNECT_CLIENT_ID")
STRIPE_DOMAIN = os.getenv("STRIPE_DOMAIN_TEST") if DEVELOPMENT_MODE is True else os.getenv("STRIPE_DOMAIN")

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler'
        },
    },
    'loggers': {
        '': {  # 'catch all' loggers by referencing it with the empty string
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
}
