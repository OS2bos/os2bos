"""
Django settings for bevillingsplatform project.

Generated by "django-admin startproject" using Django 2.2.1.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""

import os
import configparser
import logging

logger = logging.getLogger(__name__)


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

config = configparser.ConfigParser()
config["settings"] = {}


# We support loading settings from two files. The fallback values in this
# `settings.py` is first overwritten by the values defined in the file where
# the env var `DJANGO_SETTINGS_INI_PRELOAD` points to. Finally the values are
# overwritten by the values the env var `DJANGO_SETTINGS_INI` points to.
#
# The `DJANGO_SETTINGS_INI_PRELOAD` file is for an alternative set of default
# values. It is useful in a specific envionment such as Docker. An example is
# the setting for STATIC_ROOT. The default in `settings.py` is relative to the
# current directory. In Docker it should be an absolute path that is easy to
# mount a volume to.
#
# The `DJANGO_SETTINGS_INI` file is for normal settings and shoud generally be
# unique to a instance deployment.

for env in ["DJANGO_SETTINGS_INI_PRELOAD", "DJANGO_SETTINGS_INI"]:
    path = os.getenv(env, None)
    if path:
        try:
            with open(path) as fp:
                config.read_file(fp)
            logger.info("Loaded setting %s from %s" % (env, path))
        except OSError as e:
            logger.error(
                "Loading setting %s from %s failed with %s." % (env, path, e)
            )


# use settings section as default
settings = config["settings"]

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = settings.get("SECRET_KEY", fallback="Not.a.secret")

# SECURITY WARNING: don"t run with debug turned on in production!
DEBUG = settings.getboolean("DEBUG", fallback=False)

ALLOWED_HOSTS = settings.get("ALLOWED_HOSTS", fallback="").split(",")


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "django_extensions",
    "django_filters",
    "simple_history",
    "core",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    # For tracking which user made the changes for a model.
    "simple_history.middleware.HistoryRequestMiddleware",
]

ROOT_URLCONF = "bevillingsplatform.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ]
        },
    }
]


WSGI_APPLICATION = "bevillingsplatform.wsgi.application"


# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": settings.get(
            "DATABASE_ENGINE", fallback="django.db.backends.postgresql"
        ),
        "NAME": settings.get("DATABASE_NAME", fallback=""),
        "USER": settings.get("DATABASE_USER", fallback=""),
        "PASSWORD": settings.get("DATABASE_PASSWORD", fallback=""),
        "HOST": settings.get("DATABASE_HOST", fallback=""),
        "PORT": settings.getint("DATABASE_PORT", fallback=5432),
    }
}


# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation."
        "UserAttributeSimilarityValidator"
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {
        "NAME": "django.contrib.auth.password_validation."
        "CommonPasswordValidator"
    },
    {
        "NAME": "django.contrib.auth.password_validation."
        "NumericPasswordValidator"
    },
]


# Internationalization
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = "da-dk"

TIME_ZONE = "Europe/Copenhagen"

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/
STATIC_URL = "/static/"
STATIC_ROOT = settings.get(
    "STATIC_ROOT", fallback=os.path.join(BASE_DIR, "static")
)

STATICFILES_DIRS = [
    # The vue frontend code is output to this directory. `./manage.py
    # collectstatic` copies it to `STATIC_ROOT/frontend` where it it served by
    # WhiteNoise via `bevillingsplatform/urls.py`.
    ("frontend", "../frontend/dist")
]


# Serviceplatform service UUIDs
SERVICEPLATFORM_UUIDS = {
    "service_agreement": settings.get("SERVICEPLATFORM_SERVICE_AGREEMENT"),
    "user_system": settings.get("SERVICEPLATFORM_USER_SYSTEM"),
    "user": settings.get("SERVICEPLATFORM_USER"),
    "service": settings.get("SERVICEPLATFORM_SERVICE"),
}

# Serviceplatform Certificate

SERVICEPLATFORM_CERTIFICATE_PATH = settings.get(
    "SERVICEPLATFORM_CERTIFICATE_PATH"
)

REST_FRAMEWORK = {
    "DEFAULT_FILTER_BACKENDS": (
        "django_filters.rest_framework.DjangoFilterBackend",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
    ),
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ),
}

# Logging
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "default": {
            "level": "DEBUG",
            "class": "logging.FileHandler",
            "filename": settings.get(
                "LOG_FILE", fallback=os.path.join(BASE_DIR, "debug.log")
            ),
        }
    },
    "loggers": {
        "django": {"handlers": ["default"], "level": "INFO", "propagate": True}
    },
}

# Email settings
EMAIL_BACKEND = settings.get(
    "EMAIL_BACKEND", fallback="django.core.mail.backends.smtp.EmailBackend"
)
EMAIL_HOST_USER = settings.get("EMAIL_HOST_USER", fallback="")
EMAIL_HOST_PASSWORD = settings.get("EMAIL_HOST_PASSWORD", fallback="")
EMAIL_HOST = settings.get("EMAIL_HOST", fallback="")
EMAIL_PORT = settings.getint("EMAIL_PORT", fallback=25)
DEFAULT_FROM_EMAIL = settings.get(
    "DEFAULT_FROM_EMAIL", fallback="admin@bevillingsplatform-test.magenta.dk"
)
