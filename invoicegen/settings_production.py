"""
Production settings for invoicegen project.
"""
import os
from decouple import config
from .settings import *

# Security settings
DEBUG = True  # Temporalmente habilitado para debugging
SECRET_KEY = config('SECRET_KEY', default='your-secret-key-here')
ALLOWED_HOSTS = ['*']  # Permitir todos los hosts para Railway

# Database - PostgreSQL para producción
# Usar DATABASE_URL de Railway si está disponible, sino usar variables individuales
if config('DATABASE_URL', default=None):
    import dj_database_url
    DATABASES = {
        'default': dj_database_url.parse(config('DATABASE_URL'))
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': config('DB_NAME', default='invoiceapp'),
            'USER': config('DB_USER', default='postgres'),
            'PASSWORD': config('DB_PASSWORD', default=''),
            'HOST': config('DB_HOST', default='localhost'),
            'PORT': config('DB_PORT', default='5432'),
        }
    }

# Static files
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATIC_URL = '/static/'
# STATICFILES_DIRS = [
#     os.path.join(BASE_DIR, 'static'),
# ]
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Security headers (temporarily disabled for testing)
# SECURE_SSL_REDIRECT = True
# SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
# SESSION_COOKIE_SECURE = True
# CSRF_COOKIE_SECURE = True

# CSRF configuration
CSRF_TRUSTED_ORIGINS = ['https://*.railway.app']
CSRF_COOKIE_SECURE = False  # Temporalmente deshabilitado para Railway
SESSION_COOKIE_SECURE = False  # Temporalmente deshabilitado para Railway

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
    },
}
