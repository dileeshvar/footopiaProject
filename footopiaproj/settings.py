"""
Django settings for footopiaproj project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'k!*w2whb%-0f0(a1+6fm#ori%+0g=6(08)v$3#*q37@%(wxw^k'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []



# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
	'footopia',
	'kombu.transport.django',
	'djcelery'
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'footopiaproj.urls'

WSGI_APPLICATION = 'footopiaproj.wsgi.application'

LOGIN_URL = '/login'
LOGIN_REDIRECT_URL = '/home'

# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'footopia',
        'USER': 'webapps',
        'PASSWORD': 'fun',
        'HOST': 'localhost',
        'PORT': '',
    }
}

BROKER_URL = 'mongodb://localhost:27017/tasks'

# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'US/Eastern'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Media files
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/

STATIC_URL = '/static/'
# STATIC_ROOT = "/home/dil/git/Team133/footopiaproj/footopia/static/"
STATIC_ROOT = BASE_DIR + "/footopia/static/"


# Configures Django to merely print emails rather than sending them.
# Comment out this line to enable real email-sending.
#EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# To enable real email-sending, you should uncomment and
# configure the settings below.
EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'               # perhaps 'smtp.andrew.cmu.edu'
EMAIL_PORT = '587'
EMAIL_HOST_USER = 'footopiaapp@gmail.com'      # perhaps your Andrew ID
EMAIL_HOST_PASSWORD = 'footopia123'

import djcelery
djcelery.setup_loader()
BROKER_URL = 'django://'
CELERY_RESULT_BACKEND = 'djcelery.backends.database:DatabaseBackend'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'

from datetime import timedelta

CELERYBEAT_SCHEDULE = {
    'refresh-tournaments': {
        'task': 'footopia.tasks.refresh_tournaments',
        'schedule': timedelta(days=1)
    },
	'refresh-results': {
        'task': 'footopia.tasks.update_results',
        'schedule': timedelta(hours=1)
    },
}
