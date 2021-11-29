"""
Django settings for boutique_ado project.

Generated by 'django-admin startproject' using Django 3.2.9.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""

import os
import dj_database_url
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
# BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY', '')
# SECURITY WARNING: don't run with debug turned on in production!
# Here, debug will be set to true only if there's a variable called 
# 'development' in the environment.
DEBUG = 'DEVELOPMENT' in os.environ

# We'll add the hostname of our Heroku app to allowed hosts in settings.py
# & also 'localhost' so that gitpod will still work too.
ALLOWED_HOSTS = ['ebony14-boutique-ado.herokuapp.com', 'localhost']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # The 4 lines of code below should be in my MS5 project's settings.py
    'django.contrib.sites',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'home',
    'products',
    'bag',
    'checkout',
    'profiles',

    # Other
    'crispy_forms',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'boutique_ado.urls'

CRISPY_TEMPLATE_PACK = 'bootstrap4'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'templates'),
            os.path.join(BASE_DIR, 'templates', 'allauth'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',  # required by allauth
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.media',
                # We'll add the context processor created in contexts.py file
                # earlier to the list of context processors in the templates
                # variable in settings.py to make it available to the entire
                # application. What this means is that anytime we need to
                # access the bag contents in any template across the entire
                # site, they'll be available to us without having to return
                # them from a whole bunch of different views across
                # different apps.
                'bag.contexts.bag_contents',
            ],
            # To use crispy forms in a couple of templates, we have to
            # load the template tags like we load static in all our
            # templates. This becomes tedious if we want to use it all
            # over our application so instead of doing that, we'll add
            # a list called 'built-ins' underneath context processors in
            # the 'templates' setting in settings.py which will contain
            # all the tags we want available in all our templates by
            # default.
            'builtins': [
                # Adding both 'crispy forms tags' & 'crispy forms field'
                # will give us access to everything we need from crispy
                # forms across all templates by default.
                'crispy_forms.templatetags.crispy_forms_tags',
                'crispy_forms.templatetags.crispy_forms_field',
            ]
        },
    },
]

# This tells settings to store messages in the session. It's required if we use gitpod.
MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'

# This authentication backends must be in my project's settings.py file
AUTHENTICATION_BACKENDS = [
    # Needed to login by username in Django admin, regardless of `allauth`
    'django.contrib.auth.backends.ModelBackend',

    # `allauth` specific authentication methods, such as login by e-mail
    'allauth.account.auth_backends.AuthenticationBackend',
]

# This must be added to my MS5 project's settings.py file
SITE_ID = 1

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Paste these 7 lines of code below into my MS5 project's settings.py file
ACCOUNT_AUTHENTICATION_METHOD = 'username_email'
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_EMAIL_VERIFICATION = 'mandatory'
ACCOUNT_SIGNUP_EMAIL_ENTER_TWICE = True
ACCOUNT_USERNAME_MIN_LENGTH = 4
LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/'

WSGI_APPLICATION = 'boutique_ado.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

# We'll use an if statement in this section of our settings.py
# so that when our app is running on Heroku where the database URL
# environment variable will be defined, we connect to Postgres
# otherwise (i.e running locally in development environment), we
# connect to our local DB i.e sqlite.
if 'DATABASE_URL' in os.environ:
    DATABASES = {
        'default': dj_database_url.parse(os.environ.get('DATABASE_URL'))
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            # 'NAME': BASE_DIR / 'db.sqlite3',
            'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        }
    }

# DATABASES = {
#     'default': dj_database_url.parse('postgres://mexamriwwzwrif:fdaddf117d2824e8196c677935db55c6372e84e09d204b8ebbc8b5560436d63f@ec2-34-253-116-145.eu-west-1.compute.amazonaws.com:5432/d55jhkc27ficlh')
# }


# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_URL = '/static/'
# This will tell Django where all of our static files are located.
# Since they're located in the project level static folder, all we
# need to do is shown on the next line below
STATICFILES_DIRS = (os.path.join(BASE_DIR, 'static'),)

# The code on the 2 lines below this comment is where all uploaded media files will go.
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Stripe
# These 1st 2 new variables below this comment
# will be used to calculate delivery costs
FREE_DELIVERY_THRESHOLD = 50
STANDARD_DELIVERY_PERCENTAGE = 10
STRIPE_CURRENCY = 'usd'

# These next 2 variables are important & we'll get them from the environment.
# The reason is because even though the public key is already in our github
# from the last commit, we really don't want the secret key in there because
# the secret key can be used to do everything on stripe including creating
# charges, making payments, issuing refunds, & even updating our own account
# information so it's very important to keep the secret key safe & out of
# version control. Both variables will have empty default values.
STRIPE_PUBLIC_KEY = os.getenv('STRIPE_PUBLIC_KEY', '')
STRIPE_SECRET_KEY = os.getenv('STRIPE_SECRET_KEY', '')
STRIPE_WH_SECRET = os.getenv('STRIPE_WH_SECRET', '')
DEFAULT_FROM_EMAIL = 'boutiqueado@example.com'
