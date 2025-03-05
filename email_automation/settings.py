from datetime import timedelta
from pathlib import Path
import os
from dotenv import load_dotenv
import ssl
from django.core.mail import EmailMessage
import boto3
from urllib.parse import urlparse

load_dotenv()


BASE_URL = os.getenv("BASE_URL")


BASE_DIR = Path(__file__).resolve().parent.parent


ORIGINAL_TEMPLATES_DIR = BASE_DIR / "original_email_templates"
EDITED_TEMPLATES_DIR = BASE_DIR / "edited_email_templates"

EMAIL_TEMPLATES_DIR = BASE_DIR / "templates"

SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "fallback-secret-key")

DEBUG = True

ALLOWED_HOSTS = [
    "localhost",
    "127.0.0.1",
    "208.87.134.149",
    "email-automation-mocha.vercel.app",
    "backend.wishgeeksdigital.com",
    "www.wishgeeksdigital.com",
    "django-api-aqlo.onrender.com",
    "websocket-bpqt.onrender.com",
]


### esko production par uncomment krna h
###### render wale me eski jrurt nahi hai
# SESSION_COOKIE_SECURE = True
# CSRF_COOKIE_SECURE = True
# SECURE_SSL_REDIRECT = True

CSRF_TRUSTED_ORIGINS = [
    "https://django-api-aqlo.onrender.com",
    "http://208.87.134.149",
    "https://backend.wishgeeksdigital.com",
    "https://websocket-bpqt.onrender.com",
]


LOGIN_URL = "/login/"
LOGIN_REDIRECT_URL = "/login/"
LOGOUT_REDIRECT_URL = "/login/"

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
    "corsheaders",
    "authentication",
    "email_sender",
    "storages",
    "channels",
    "subscriptions",
]

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticated",),
}






RAZORPAY_KEY_ID = os.getenv("RAZORPAY_KEY_ID")
RAZORPAY_SECRET_KEY = os.getenv("RAZORPAY_SECRET_KEY")

VERIFY_URL = os.getenv("VERIFY_URL")
MERCHANT_ID = os.getenv("MERCHANT_ID")
PHONEPE_URL = os.getenv("PHONEPE_URL")
SALT_KEY = os.getenv("SALT_KEY")

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(days=1),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=35),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "ALGORITHM": "HS256",
    "SIGNING_KEY": "your-secret-key",
    "VERIFYING_KEY": None,
    "AUTH_HEADER_TYPES": ("Bearer",),
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
    "BLACKLIST_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.RefreshToken",),
}


MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    # 'django.middleware.csrf.CsrfViewMiddleware',
    # 'channels.middleware.WebSocketMiddleware',
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://wishgeeksdigital.com",
    "https://email-automation-mocha.vercel.app",
]


CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

SESSION_COOKIE_AGE = 1209600  # Two weeks
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

# PASSWORD_RESET_TIMEOUT = 3600  #1 hr


ROOT_URLCONF = "email_automation.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

ASGI_APPLICATION = "email_automation.asgi.application"


##### ye wala DB use krna h render wale server per to esko uncomment krke niche vale ko comment krke deploy krna h
import dj_database_url

DATABASES = {"default": {}}

database_url = os.environ.get("DATABASE_URL")
DATABASES["default"] = dj_database_url.parse(database_url)

# DATABASES = {
#     'default': {
#         'ENGINE': os.getenv('DB_ENGINE'),
#         'NAME': os.getenv('DB_NAME'),
#         'USER': os.getenv('DB_USER'),
#         'PASSWORD': os.getenv('DB_PASSWORD'),
#         'HOST': os.getenv('DB_HOST'),
#         'PORT': os.getenv('DB_PORT'),
#     }
# }


DATABASE_ROUTERS = ["authentication.database_router.DatabaseRouter"]


AUTHENTICATION_BACKENDS = [
    "authentication.backends.EmailBackend",
    "django.contrib.auth.backends.ModelBackend",
]


AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "Asia/Kolkata"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_STORAGE_BUCKET_NAME = os.getenv("AWS_STORAGE_BUCKET_NAME")
AWS_S3_REGION_NAME = os.getenv("AWS_S3_REGION_NAME")


DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"

AWS_DEFAULT_ACL = None

AWS_QUERYSTRING_AUTH = False


AWS_S3_CUSTOM_DOMAIN = f"{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com"
AWS_S3_FILE_URL = f"https://{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com/"


MEDIA_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

# MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
# MEDIA_URL = '/media/'

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = os.getenv("EMAIL_HOST")
EMAIL_PORT = os.getenv("EMAIL_PORT")
EMAIL_USE_TLS = True
# EMAIL_USE_SSL = False  # Commented out as not used
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
ADMIN_EMAIL = EMAIL_HOST_USER
# DEFAULT_FROM_EMAIL = EMAIL_HOST_USER


class SSLDisableContext:
    def __enter__(self):
        self.ssl_context = ssl._create_unverified_context()
        self.original_get_connection = get_connection

        def get_connection(backend=None, fail_silently=False, **kwargs):
            return self.original_get_connection(
                backend, fail_silently, ssl_context=self.ssl_context, **kwargs
            )

        EmailMessage.get_connection = staticmethod(get_connection)

    def __exit__(self, exc_type, exc_value, traceback):
        EmailMessage.get_connection = staticmethod(self.original_get_connection)


SSLDisableContext()

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
        },
    },
    "loggers": {
        "django.core.mail": {
            "handlers": ["console"],
            "level": "DEBUG",
        },
    },
}


CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer",
    },
}

# import os
# from urllib.parse import urlparse

# # Fetch the Redis URL from the environment variable
# redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379')  # Default to localhost for local development

# # Parse the Redis URL
# url = urlparse(redis_url)

# Configure Channels to use Redis
# CHANNEL_LAYERS = {
#     'default': {
#         'BACKEND': 'channels_redis.core.RedisChannelLayer',
#         'CONFIG': {
#             'hosts': [(url.hostname, url.port, {
#                 # 'password': url.password,  # No password in your case, so this should be None
#                 'db': 0  # Default Redis DB
#             })],
#         },
#     },
# }


# CHANNEL_LAYERS = {
#     'default': {
#         'BACKEND': 'channels_redis.core.RedisChannelLayer',
#         'CONFIG': {
#             'hosts': [
#                 'redis://:admin@123@0.0.0.0:6379',
#             ],
#         },
#     },
# }
