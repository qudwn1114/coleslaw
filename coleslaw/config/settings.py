from pathlib import Path
import os, yaml

CONFIG_FILE = './config/conf.yaml'
with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
    config = yaml.load(f, Loader=yaml.FullLoader)

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config['SECRET_KEY']

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config['DEBUG']

ALLOWED_HOSTS = config['ALLOWED_HOSTS']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    
    #cors
    'corsheaders',
    #channels
    'channels',
    # restframework
    'rest_framework',

    #app
    'agency',
    'api',
    'system_manage',
    'shop_manage',
    'entry',
    'notification'
]

ASGI_APPLICATION = 'config.asgi.application'

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [('localhost', 6379)],
        },
    },
}

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

CORS_ORIGIN_ALLOW_ALL = True

# CORS_ORIGIN_WHITELIST = []

CORS_ALLOW_CREDENTIALS = True

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR,'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'config.template_global_variables.global_variables',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': config['DATABASE']['ENGINE'],
        'NAME': config['DATABASE']['NAME'],
        'USER': config['DATABASE']['USER'],
        'PASSWORD': config['DATABASE']['PASSWORD'],
        'HOST': config['DATABASE']["HOST"],
        'PORT': config['DATABASE']['PORT'],
        'OPTIONS': {
            'charset': 'utf8mb4',
        },
    },
}


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'ko-kr'

TIME_ZONE = 'Asia/Seoul'

USE_I18N = True

USE_L10N = True

USE_TZ = False

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.0/howto/static-files/
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, '.static_root')

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOG_DIR = "logs/"
if not os.path.isdir(LOG_DIR):
    os.mkdir(LOG_DIR)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    "filters": {
        "require_debug_false": {"()": "django.utils.log.RequireDebugFalse"},
        "require_debug_true": {"()": "django.utils.log.RequireDebugTrue"},
    },
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}\n',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {asctime} {message}',
            'style': '{',
        }
    },
    'handlers': {
        'file': {  # Daily log to file.
            'level': 'ERROR',
            'formatter': 'verbose',
            'filename': os.path.join(LOG_DIR, 'mysite.log'),
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'when': 'midnight',
            'interval': 1,
        },
        'console': {
            'level': 'INFO',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'propagate': False,
        },
        # my log 사용법
        # import logging, traceback
        # logger = logging.getLogger('my')
        # logger.error(traceback.format_exc())
        'my': {
            'handlers': ['console', 'file'],
            'level': 'ERROR',
            'propagate': False
        },
    }
}


SITE_URL = config['SITE_URL']
SITE_NAME = config['SITE_NAME']


SMS_ACCESS_KEY = config['SMS_ACCESS_KEY']
SMS_SECRET_KEY = config['SMS_SECRET_KEY']
SMS_API_KEY = config['SMS_API_KEY']
SMS_SENDER = config['SMS_SENDER']