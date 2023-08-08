# Third party
from decouple import config

# Local
from settings.base import *  # noqa

# ----------------------------------------------
#
DEBUG = False
WSGI_APPLICATION = 'deploy.prod.wsgi.application'
ASGI_APPLICATION = 'deploy.prod.asgi.application'

# ----------------------------------------------
#
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config("DB_NAME", cast=str),
        'USER': config("DB_USER", cast=str),
        'PASSWORD': config("DB_POSTGRESQL_PASSWORD", cast=str),
        'HOST': config("DB_HOST", cast=str),
        'PORT': config("DB_PORT", cast=int)
    }
}
ALLOWED_HOSTS = [
    "127.0.0.1",
    "localhost",
]
INTERNAL_IPS = [
    "127.0.0.1",
]
