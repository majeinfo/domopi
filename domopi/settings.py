"""
Django settings for domopi project.

Generated by 'django-admin startproject' using Django 1.8.5.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.8/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
import mongoengine
#import mongo_auth
#import mongo_sessions

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.8/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'c@68%peh$sli5^^h!qk+#kwtkf3(!fem3cebi)r34z37@-0!i%'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    #'mongoengine.django.mongo_auth',
    #'mongo_auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    #'mongo_auth.middleware.LazyUserMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
)

ROOT_URLCONF = 'domopi.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [ os.path.join(BASE_DIR, 'frontend/templates') ],
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

WSGI_APPLICATION = 'domopi.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases

DATABASES = {
    'default': {
        #'ENGINE': 'django.db.backends.sqlite3',
        #'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        'ENGINE': 'django.db.backends.mysql',
        'HOST': 'localhost',
        'USER': 'domopi',
        'PASSWORD': 'domopi',
        'NAME': 'domopi',
    }
}


# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/

LANGUAGE_CODE = 'fr-fr'

TIME_ZONE = 'Europe/Paris'

USE_I18N = True

USE_L10N = True

USE_TZ = True

LOGIN_URL = '/frontend/auth/login'


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/

STATIC_URL = '/static/'

_MONGODB_USER = 'domopi'
_MONGODB_PASSWORD = 'domopi'
_MONGODB_HOST = 'localhost'
_MONGODB_NAME = 'domopi'
_MONGODB_DATABASE_HOST = 'mongodb://%s:%s@%s/%s' % (_MONGODB_USER, _MONGODB_PASSWORD, _MONGODB_HOST, _MONGODB_NAME)

mongoengine.connect(_MONGODB_NAME, host=_MONGODB_DATABASE_HOST)

#SESSION_ENGINE = 'mongo_sessions.session'

#MONGO_PORT = 27017
#MONGO_HOST = _MONGODB_HOST
#MONGO_DB_NAME = _MONGODB_NAME
#MONGO_DB_USER = _MONGODB_USER
#MONGO_DB_PASSWORD = _MONGODB_PASSWORD
#MONGO_SESSIONS_COLLECTION = 'mongo_sessions'
#MONGO_SESSIONS_TTL = 60 * 15

AUTHENTIFICATION_BACKENDS = (
    #'mongoengine.django.auth.MongoEngineBackend',
    #'mongo_auth.backends.MongoEngineBackend',
)
#MONGOENGINE_USER_DOCUMENT = 'mongoengine.django.auth.User'
#AUTH_USER_MODEL = 'mongo_auth.MongoUser'
#USER_CLASS = 'mongo_auth.contrib.models.Use'