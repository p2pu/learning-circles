"""
Django settings for learnwithpeople project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
path = lambda *a: os.path.join(BASE_DIR, *a)
env = lambda key, default: os.environ.get(key, default)


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

ADMINS = (
    ('Admin', os.environ.get('ADMIN_EMAIL', 'admin@localhost') ),
)

COMMUNITY_MANAGER = os.environ.get('COMMUNITY_MANAGER_EMAIL', 'community@localhost')


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY', 'youshouldchangethis')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DEBUG', False) == 'true'
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
    'corsheaders',
    'crispy_forms',
    'phonenumber_field',
    'rest_framework',
    'django_filters',
    'webpack_loader',
    # own
    'studygroups',
    'backup',
    'analytics',
    'uxhelpers',
    'custom_registration',
    'advice',
    'surveys',
    'announce',
    'community_calendar',
    'client_logging',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

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

FORMAT_MODULE_PATH = [
    'learnwithpeople.formats',
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
                'studygroups.context_processors.domain',
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

#CRISPY_TEMPLATE_PACK = 'bootstrap3'
CRISPY_TEMPLATE_PACK = 'bootstrap4'

EMAIL_HOST = os.environ.get('EMAIL_HOST')
EMAIL_PORT = os.environ.get('EMAIL_PORT', 25)
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')

if DEBUG is True and EMAIL_HOST is None:
    EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
    EMAIL_FILE_PATH = path('mailbox')

# Default email sender
DEFAULT_FROM_EMAIL = env('DEFAULT_FROM_EMAIL', 'webmaster@localhost')

# email for sending the community digest to
COMMUNITY_DIGEST_EMAIL = env('COMMUNITY_DIGEST_EMAIL', 'digest@localhost')

# Used for error messages to admin/staff
SERVER_EMAIL = env('SERVER_EMAIL', 'no-reply@p2pu.org')

# Team email
TEAM_EMAIL = env('TEAM_EMAIL', 'thepeople@p2pu.org')

##### Database config
import dj_database_url
DATABASES['default'] =  dj_database_url.config(default='sqlite:///{0}'.format(path('db.sqlite3')))

# Honor the 'X-Forwarded-Proto' header for request.is_secure()
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Allow all host headers
ALLOWED_HOSTS = ['*']

# CORS config
CORS_ORIGIN_WHITELIST = [
    "https://www.p2pu.org",
    "https://berlin.p2pu.org",
    "http://berlin.p2pu.org",
    "https://p2pu.github.io",
]
if DEBUG:
    CORS_ORIGIN_WHITELIST.append('http://localhost:8000')

AUTHENTICATION_BACKENDS = ['custom_registration.backend.CaseInsensitiveBackend']

##### Twilio config

TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN')
TWILIO_NUMBER = os.environ.get('TWILIO_NUMBER')

LOGIN_REDIRECT_URL = '/login_redirect/'
LOGOUT_REDIRECT_URL = 'https://www.p2pu.org/en/facilitate/'
DOMAIN = env('DOMAIN', 'localhost:8000')
PROTOCOL = env('PROTOCOL', 'https')

####### Google analytics tracking info #######
GA_TRACKING_ID = env('GA_TRACKING_ID', 'UA-0000000-00')

####### Celery config #######
BROKER_URL = env('BROKER_URL', 'amqp://guest:guest@localhost//')


from celery.schedules import crontab

CELERYBEAT_SCHEDULE = {
    'gen_reminders': {
        'task': 'studygroups.tasks.gen_reminders',
        'schedule': crontab(minute='5'),
    },
    'send_reminders': {
        'task': 'studygroups.tasks.send_reminders',
        'schedule': crontab(minute='5'),
    },
    'send_new_user_email': {
        'task': 'custom_registration.tasks.send_new_user_emails',
        'schedule': crontab(minute='*/10'),
    },
    'send_survey_reminders': {
        'task': 'studygroups.tasks.send_all_studygroup_survey_reminders',
        'schedule': crontab(minute='30'),
    },
    'send_facilitator_survey': {
        'task': 'studygroups.tasks.send_all_facilitator_surveys',
        'schedule':  crontab(minute='30'),
    },
    'send_last_week_group_activity': {
        'task': 'studygroups.tasks.send_all_last_week_group_activities',
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
    'sync_typeform_surveys': {
        'task': 'surveys.tasks.sync_surveys',
        'schedule': crontab(minute='10'),
    },
    'send_facilitator_survey_reminder': {
        'task': 'studygroups.tasks.send_all_facilitator_survey_reminders',
        'schedule': crontab(minute='30'),
    },
    'send_final_learning_circle_report': {
        'task': 'studygroups.tasks.send_all_learning_circle_reports',
        'schedule': crontab(minute='30'),
    },
    'send_community_digest': {
        'task': 'studygroups.tasks.send_out_community_digest',
        'schedule': crontab(day_of_week='monday', hour=11, minute=0),
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
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'DEBUG' if DEBUG else 'WARNING',
        },
    },
    'root': {
        'handlers': ['mail_admins', 'console'],
        'level': 'DEBUG',
    },
    'loggers': {
        'django': {
            'handlers': ['mail_admins', 'console'],
            'level': 'WARNING',
            'propagate': False,
        },
    },
}

# Disable django's default logging
LOGGING_CONFIG = None
import logging.config
logging.config.dictConfig(LOGGING)

#### Backup config ####

BACKUP_DIR = os.environ.get('BACKUP_DIR', '/tmp') # Directory where backups will be stored locally
BACKUP_AWS_ACCESS_KEY_ID = os.environ.get('BACKUP_AWS_ACCESS_KEY_ID') # AWS key with access to backup bucket
BACKUP_AWS_SECRET_ACCESS_KEY = os.environ.get('BACKUP_AWS_SECRET_ACCESS_KEY') # AWS secret for above key
BACKUP_AWS_STORAGE_BUCKET_NAME = os.environ.get('BACKUP_AWS_STORAGE_BUCKET_NAME') # Name of the bucket where backups should be stored
BACKUP_AWS_KEY_PREFIX = os.environ.get('BACKUP_AWS_KEY_PREFIX') # Prefix for generated key on AWS s3

#### Mailchimp API key ###
MAILCHIMP_API_KEY = env('MAILCHIMP_API_KEY', '')
MAILCHIMP_LIST_ID = env('MAILCHIMP_LIST_ID', '')
MAILCHIMP_API_ROOT = env('MAILCHIMP_API_ROOT', 'https://??.api.mailchimp.com/3.0/')

DISCOURSE_BASE_URL = env('DISCOURSE_BASE_URL', 'https://community.p2pu.org')
DISCOURSE_SSO_SECRET = env('DISCOURSE_SSO_SECRET', '')
DISCOURSE_API_KEY = env('DISCOURSE_API_KEY', '')
DISCOURSE_API_USERNAME = env('DISCOURSE_API_USERNAME', '')
DISCOURSE_BOT_API_KEY = env('DISCOURSE_BOT_API_KEY', '')
DISCOURSE_BOT_API_USERNAME = env('DISCOURSE_BOT_API_USERNAME', '')
DISCOURSE_COURSES_AND_TOPICS_CATEGORY_ID = env('DISCOURSE_COURSES_AND_TOPICS_CATEGORY_ID', 69)

TYPEFORM_ACCESS_TOKEN = env('TYPEFORM_ACCESS_TOKEN', '')
TYPEFORM_FACILITATOR_SURVEY_FORM = env('TYPEFORM_FACILITATOR_SURVEY_FORM', '')
TYPEFORM_LEARNER_SURVEY_FORM = env('TYPEFORM_LEARNER_SURVEY_FORM', '')

# AWS credentials for email resources
P2PU_RESOURCES_AWS_ACCESS_KEY = env('RESOURCES_AWS_ACCESS_KEY', '')
P2PU_RESOURCES_AWS_SECRET_KEY = env('RESOURCES_AWS_SECRET_KEY', '')
P2PU_RESOURCES_AWS_BUCKET = env('RESOURCES_AWS_BUCKET', '')

# Config for sending announcements
MAILGUN_API_KEY = env('MAILGUN_API_KEY', '')
MAILGUN_DOMAIN = env('MAILGUN_DOMAIN', '')
ANNOUNCE_EMAIL = env('ANNOUNCE_EMAIL', 'announce@localhost')

# Instagram token
INSTAGRAM_TOKEN = env('INSTAGRAM_TOKEN', '')

REST_FRAMEWORK = {
    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'PAGE_SIZE': 10,
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly'
    ],
    'DEFAULT_FILTER_BACKENDS': ['django_filters.rest_framework.DjangoFilterBackend']
}
