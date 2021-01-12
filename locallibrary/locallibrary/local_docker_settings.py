"""
Production Settings for Heroku

In config vars set as:
key:DJANGO_SETTINGS_MODULE
value:locallibrary.production_settings
"""

from .development_settings import *

# In production, add actual DNS and IP address here
ALLOWED_HOSTS = ['127.0.0.1', ]

# Parse database connection url strings like psql://user:pass@127.0.0.1:8458/db
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.getenv('POSTGRES_DB'),
        'USER': os.getenv('POSTGRES_USER'),
        'PASSWORD': os.getenv('POSTGRES_PASSWORD'),
        'HOST': os.getenv('POSTGRES_HOST'),
        'PORT': os.getenv('POSTGRES_PORT'),
    }
}