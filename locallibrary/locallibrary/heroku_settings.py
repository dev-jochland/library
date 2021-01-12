"""
Production Settings for Heroku

In config vars set as:
key:DJANGO_SETTINGS_MODULE
value:locallibrary.production_settings
"""

from .development_settings import *

# Raises django's ImproperlyConfigured exception if SECRET_KEY not in os.environ
SECRET_KEY = env.str('SECRET_KEY')

ALLOWED_HOSTS = ['.herokuapp.com', ]

# Parse database connection url strings like psql://user:pass@127.0.0.1:8458/db
DATABASES = {
    # read os.environ['DATABASE_URL'] and raises ImproperlyConfigured exception if not found
    'default': env.db('DATABASE_URL'),
}
