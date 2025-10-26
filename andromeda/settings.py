from pathlib import Path
import os
from dotenv import load_dotenv

try:
    import dj_database_url
except ImportError:
    dj_database_url = None

BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables from .env file
load_dotenv(os.path.join(BASE_DIR, '.env'))

SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-change-me')
DEBUG = os.environ.get('DEBUG', 'True').lower() == 'true'
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1,0.0.0.0').split(',')

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'core',
    # New apps
    'meditation',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'andromeda.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'core', 'templates')],
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

WSGI_APPLICATION = 'andromeda.wsgi.application'

DATABASES = {
    'default': dj_database_url.config(default=f'sqlite:///{BASE_DIR / "db.sqlite3"}') if dj_database_url else {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = []

AUTH_USER_MODEL = 'core.User'

# Custom authentication backend to allow login with email or username
AUTHENTICATION_BACKENDS = [
    'core.backends.EmailOrUsernameModelBackend',
    'django.contrib.auth.backends.ModelBackend',
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'

# Media files (uploads)
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Channels / ASGI (optional)
# Channels is optional so local environments that don't have 'channels' installed
# can still run tests and Django checks. To enable channels set USE_CHANNELS=1
# in your environment and optionally set CHANNEL_REDIS_URL to a redis:// url.
USE_CHANNELS = os.environ.get('USE_CHANNELS', '0') in ('1', 'True', 'true', 'yes')
if USE_CHANNELS:
    try:
        import channels  # noqa: F401
        INSTALLED_APPS.append('channels')
        ASGI_APPLICATION = 'andromeda.asgi.application'

        # If CHANNEL_REDIS_URL is set, use Redis backend; otherwise fall back to in-memory.
        CHANNEL_REDIS_URL = os.environ.get('CHANNEL_REDIS_URL')
        if CHANNEL_REDIS_URL:
            CHANNEL_LAYERS = {
                'default': {
                    'BACKEND': 'channels_redis.core.RedisChannelLayer',
                    'CONFIG': {
                        'hosts': [CHANNEL_REDIS_URL],
                    },
                }
            }
        else:
            CHANNEL_LAYERS = {
                'default': {
                    'BACKEND': 'channels.layers.InMemoryChannelLayer'
                }
            }
    except Exception:
        # channels isn't installed; leave Channels disabled.
        USE_CHANNELS = False

# Redirect URLs
LOGIN_REDIRECT_URL = '/dashboard/'
LOGOUT_REDIRECT_URL = '/accounts/login/'
LOGIN_URL = '/accounts/login/'

# AI API Configuration
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
GROK_API_KEY = os.environ.get('GROK_API_KEY')
GOOGLE_VISION_API_KEY = os.environ.get('GOOGLE_VISION_API_KEY')

# AI Service Settings
AI_TEXT_MODEL = os.environ.get('AI_TEXT_MODEL', 'gpt-4o-mini')
AI_VISION_MODEL = os.environ.get('AI_VISION_MODEL', 'gpt-4o-mini')

# Email Configuration
EMAIL_BACKEND = os.environ.get('EMAIL_BACKEND', 'django.core.mail.backends.console.EmailBackend')
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 587))
EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', 'True').lower() == 'true'
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'noreply@andromeda.com')