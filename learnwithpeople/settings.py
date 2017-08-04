"""
Django settings for learnwithpeople project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""
from __future__ import absolute_import

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
path = lambda *a: os.path.join(BASE_DIR, *a)

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

ADMINS = (
    ('Admin', os.environ.get('ADMIN_EMAIL', 'admin@localhost') ),
)

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY', 'youshouldchangethis')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False
CRISPY_FAIL_SILENTLY = not DEBUG

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    # 3rd party apps
    'crispy_forms',
    'phonenumber_field',
    # own
    'studygroups',
    'api',
    'backup',
    'analytics',
    'uxhelpers',
    'webpack_loader',
]

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'learnwithpeople.urls'

WSGI_APPLICATION = 'learnwithpeople.wsgi.application'


# Database

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = 'en'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


LOCALE_PATHS = [
    path('locale')
]

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/

STATIC_URL = '/static/'

STATIC_ROOT = path('static_serve')

STATICFILES_DIRS = [
    path('static'),
    path('assets'),
]

STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    # other finders..
]

MEDIA_URL = '/media/'
MEDIA_ROOT = path('upload')

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'APP_DIRS': True,
        'DIRS': [path('templates')],
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ]
        }
    },
]


####### Django Webpack Loader config #######
WEBPACK_LOADER = {
    'DEFAULT': {
        'BUNDLE_DIR_NAME': 'dist/',
        'STATS_FILE': path('assets/frontend-webpack-manifest.json'),
    },
    'STYLEBUILD': {
        'BUNDLE_DIR_NAME': 'dist/',
        'STATS_FILE': path('assets/style-webpack-manifest.json'),
    },
}

CRISPY_TEMPLATE_PACK = 'bootstrap3'

EMAIL_HOST = os.environ.get('EMAIL_HOST')
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')

DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'webmaster@localhost')
SERVER_EMAIL = os.environ.get('SERVER_EMAIL', 'no-reply@p2pu.org') #TODO grab this from environment

##### Database config
import dj_database_url
DATABASES['default'] =  dj_database_url.config(default='sqlite:///{0}'.format(path('db.sqlite3')))

# Honor the 'X-Forwarded-Proto' header for request.is_secure()
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Allow all host headers
ALLOWED_HOSTS = ['*']

AUTHENTICATION_BACKENDS = ['studygroups.backend.CaseInsensitiveBackend']

##### Twilio config

TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN')
TWILIO_NUMBER = os.environ.get('TWILIO_NUMBER')

LOGIN_REDIRECT_URL = '/login_redirect/'
DOMAIN = os.environ.get('DOMAIN', 'example.net')

####### Google analytics tracking info ####### 
GA_TRACKING_ID = os.environ.get('GA_TRACKING_ID', 'UA-0000000-00')

####### Celery config #######
BROKER_URL = os.environ.get('BROKER_URL', 'amqp://guest:guest@localhost//')


from celery.schedules import crontab

CELERYBEAT_SCHEDULE = {
    # Executes every Monday morning at 7:30 A.M
    'gen_reminders': {
        'task': 'studygroups.tasks.gen_reminders',
        'schedule': crontab(minute='*/10'),
    },
    'send_reminders': {
        'task': 'studygroups.tasks.send_reminders',
        'schedule': crontab(minute='*/10'),
    },
    'send_new_facilitator_email': {
        'task': 'studygroups.tasks.send_new_facilitator_emails',
        'schedule': crontab(hour='12', minute='0'),
    },
    'send_new_studygroup_email': {
        'task': 'studygroups.tasks.send_new_studygroup_emails',
        'schedule': crontab(hour='12', minute='0'),
    },
    'send_survey_reminders': {
        'task': 'studygroups.tasks.send_all_studygroup_survey_reminders',
        'schedule': crontab(minute='*/15'),
    },
    'send_facilitator_survey': {
        'task': 'studygroups.tasks.send_all_facilitator_surveys',
        'schedule':  crontab(hour='10', minute='0'),
    },
    'weekly_update': {
        'task': 'studygroups.tasks.weekly_update',
        'schedule': crontab(hour=10, minute=0, day_of_week='monday'),
    },
    'daily_backup': {
        'task': 'backup.tasks.make_backup',
        'schedule': crontab(hour=1, minute=0),
    },
}

LOGGING = {
    'version': 1,
    'dissable_existing_loggers': False,
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
            'include_html': True,
        },
    },
    'loggers': {
        '': {
            'handlers': ['mail_admins'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'django': {
            'handlers': ['mail_admins'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}

#### Backup config ####

BACKUP_DIR = os.environ.get('BACKUP_DIR', '/tmp') # Directory where backups will be stored locally
BACKUP_AWS_ACCESS_KEY_ID = os.environ.get('BACKUP_AWS_ACCESS_KEY_ID') # AWS key with access to backup bucket
BACKUP_AWS_SECRET_ACCESS_KEY = os.environ.get('BACKUP_AWS_SECRET_ACCESS_KEY') # AWS secret for above key
BACKUP_AWS_STORAGE_BUCKET_NAME = os.environ.get('BACKUP_AWS_STORAGE_BUCKET_NAME') # Name of the bucket where backups should be stored
BACKUP_AWS_KEY_PREFIX = os.environ.get('BACKUP_AWS_KEY_PREFIX') # Prefix for generated key on AWS s3


##### Support for settings_local.py
try:
    from .settings_local import *
except ImportError:
    pass
