"""PythonAnywhere settings for https://finaccount.pythonanywhere.com"""

import os

from .settings import *  # noqa: F403
from .settings import BASE_DIR

DEBUG = False

SECRET_KEY = os.environ.get('SECRET_KEY', '')
if not SECRET_KEY or SECRET_KEY.startswith('django-insecure'):
    raise ValueError('Set a long random SECRET_KEY in the PythonAnywhere .env file.')

ALLOWED_HOSTS = ['finaccount.pythonanywhere.com']
CSRF_TRUSTED_ORIGINS = ['https://finaccount.pythonanywhere.com']

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
