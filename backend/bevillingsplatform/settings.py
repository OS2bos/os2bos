# Copyright (C) 2019 Magenta ApS, http://magenta.dk.
# Contact: info@magenta.dk.
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.


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

from django.utils.translation import gettext_lazy as _

logger = logging.getLogger(__name__)


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

config = configparser.ConfigParser()
config["settings"] = {}


# Our customized user model
AUTH_USER_MODEL = "core.User"

# We support loading settings from two files. The fallback values in this
# `settings.py` is first overwritten by the values defined in the file where
# the env var `BEV_SYSTEM_CONFIG_PATH` points to. Finally the values are
# overwritten by the values the env var `BEV_USER_CONFIG_PATH` points to.
#
# The `BEV_SYSTEM_CONFIG_PATH` file is for an alternative set of default
# values. It is useful in a specific envionment such as Docker. An example is
# the setting for STATIC_ROOT. The default in `settings.py` is relative to the
# current directory. In Docker it should be an absolute path that is easy to
# mount a volume to.
#

# The `BEV_USER_CONFIG_PATH` file is for normal settings and shoud generally be
# unique to a instance deployment.

for env in ["BEV_SYSTEM_CONFIG_PATH", "BEV_USER_CONFIG_PATH"]:
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
SECRET_KEY = settings.get("SECRET_KEY")

# SECURITY WARNING: don"t run with debug turned on in production!
DEBUG = settings.getboolean("DEBUG", fallback=False)

ALLOWED_HOSTS = settings.get("ALLOWED_HOSTS", fallback="").split(",")

USE_X_FORWARDED_HOST = settings.getboolean(
    "USE_X_FORWARDED_HOST", fallback=True
)
SECURE_PROXY_SSL_HEADER = (
    tuple(settings.get("SECURE_PROXY_SSL_HEADER").split(","))
    if "SECURE_PROXY_SSL_HEADER" in settings
    else ("HTTP_X_FORWARDED_PROTO", "https")
)

INITIALIZE_DATABASE = settings.getboolean(
    "INITIALIZE_DATABASE", fallback=False,
)

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
    "rest_framework_filters",
    "simple_history",
    "constance",
    "constance.backends.database",
    "core.apps.CoreConfig",
    "django_saml2_auth",
    "mailer",
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
STATIC_URL = "/api/static/"
STATIC_ROOT = settings.get(
    "STATIC_ROOT", fallback=os.path.join(BASE_DIR, "static")
)

STATICFILES_DIRS = [
    # The vue frontend code is output to this directory. `./manage.py
    # collectstatic` copies it to `STATIC_ROOT/frontend` where it it served by
    # WhiteNoise via `bevillingsplatform/urls.py`.
    ("frontend", "../frontend/dist")
]

# Whether we use Serviceplatformen or a mocked version
USE_SERVICEPLATFORM = settings.getboolean(
    "USE_SERVICEPLATFORM", fallback=False
)
# Whether we use the Serviceplatformen prod or test endpoint
USE_SERVICEPLATFORM_PROD = settings.getboolean(
    "USE_SERVICEPLATFORM_PROD", fallback=False
)

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
        "rest_framework_filters.backends.RestFrameworkFilterBackend",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
    ),
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework.authentication.SessionAuthentication",
    ),
    # Let each view determine whether pagination should be used or not.
    "DEFAULT_PAGINATION_CLASS": None,
    "PAGE_SIZE": 50,
}

# Output directory for integration with KMD Prisme.
PRISM_OUTPUT_DIR = settings.get(
    "PRISM_OUTPUT_DIR", fallback=os.path.join(BASE_DIR, "prisme")
)


# Output directory for payments reports.
PAYMENTS_REPORT_DIR = settings.get(
    "PAYMENTS_REPORT_DIR", fallback=os.path.join(BASE_DIR, "reports")
)

# Logging
LOG_DIR = settings.get("LOG_DIR", fallback=os.path.join(BASE_DIR, "log"))

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "default": {
            "level": "DEBUG",
            "class": "logging.FileHandler",
            "formatter": "verbose",
            "filename": settings.get(
                "LOG_FILE", fallback=os.path.join(LOG_DIR, "django-debug.log")
            ),
        },
        "audit": {
            "level": "INFO",
            "class": "logging.FileHandler",
            "formatter": "verbose",
            "filename": settings.get(
                "AUDIT_LOG_FILE", fallback=os.path.join(LOG_DIR, "audit.log")
            ),
        },
        "export_to_prism": {
            "level": "INFO",
            "class": "logging.FileHandler",
            "formatter": "verbose",
            "filename": settings.get(
                "PRISM_LOG_FILE",
                fallback=os.path.join(LOG_DIR, "export_to_prism.log"),
            ),
        },
        "generate_payments_report": {
            "level": "INFO",
            "class": "logging.FileHandler",
            "formatter": "verbose",
            "filename": settings.get(
                "PAYMENTS_REPORT_LOG_FILE",
                fallback=os.path.join(LOG_DIR, "generate_payments_report.log"),
            ),
        },
        "mark_fictive_payments_paid": {
            "level": "INFO",
            "class": "logging.FileHandler",
            "formatter": "verbose",
            "filename": settings.get(
                "FICTIVE_PAYMENTS_LOG_FILE",
                fallback=os.path.join(
                    LOG_DIR, "mark_fictive_payments_paid.log"
                ),
            ),
        },
        "send_expired_emails": {
            "level": "INFO",
            "class": "logging.FileHandler",
            "formatter": "verbose",
            "filename": settings.get(
                "SEND_EXPIRED_EMAILS_LOG_FILE",
                fallback=os.path.join(LOG_DIR, "send_expired_emails.log"),
            ),
        },
    },
    "formatters": {
        "verbose": {
            "format": "%(levelname)s %(asctime)s %(module)s: %(message)s"
        }
    },
    "loggers": {
        "django": {
            "handlers": ["default"],
            "level": "INFO",
            "propagate": True,
        },
        "bevillingsplatform.audit": {
            "handlers": ["audit"],
            "level": "INFO",
            "propagate": True,
        },
        "bevillingsplatform.export_to_prism": {
            "handlers": ["export_to_prism"],
            "level": "INFO",
            "propagate": True,
        },
        "bevillingsplatform.generate_payments_report": {
            "handlers": ["generate_payments_report"],
            "level": "INFO",
            "propagate": True,
        },
        "bevillingsplatform.mark_fictive_payments_paid": {
            "handlers": ["mark_fictive_payments_paid"],
            "level": "INFO",
            "propagate": True,
        },
        "bevillingsplatform.send_expired_emails": {
            "handlers": ["send_expired_emails"],
            "level": "INFO",
            "propagate": True,
        },
    },
}

# Email settings
EMAIL_BACKEND = "mailer.backend.DbBackend"
EMAIL_HOST_USER = settings.get("EMAIL_HOST_USER", fallback="")
EMAIL_HOST_PASSWORD = settings.get("EMAIL_HOST_PASSWORD", fallback="")
EMAIL_HOST = settings.get("EMAIL_HOST", fallback="")
EMAIL_PORT = settings.getint("EMAIL_PORT", fallback=25)

# Django-mailer setting
MAILER_LOCK_PATH = settings.get("MAILER_LOCK_PATH", fallback="/tmp/send_mail")

# We use Constance for being able to set live settings
# (settings on the fly from Django admin).
# The defaults are loaded from the settings INI file.
CONSTANCE_CONFIG = {
    "SBSYS_EMAIL": (
        settings.get(
            "SBSYS_EMAIL", fallback="admin@bevillingsplatform-test.magenta.dk"
        ),
        _("modtager af SBSYS emails"),
    ),
    "TO_EMAIL_FOR_PAYMENTS": (
        settings.get(
            "TO_EMAIL_FOR_PAYMENTS",
            fallback="admin@bevillingsplatform-test.magenta.dk",
        ),
        _("modtager af betalings emails"),
    ),
    "DEFAULT_FROM_EMAIL": (
        settings.get(
            "DEFAULT_FROM_EMAIL",
            fallback="admin@bevillingsplatform-test.magenta.dk",
        ),
        _("fra-email"),
    ),
    "DEFAULT_TEAM_NAME": (
        settings.get(
            "DEFAULT_TEAM_NAME", fallback="Afventer tildeling af team"
        ),
        _("første team for nye brugere"),
    ),
    "ACCOUNT_NUMBER_DEPARTMENT": (
        settings.get("ACCOUNT_NUMBER_DEPARTMENT", fallback="12345"),
        _("Kontostreng afdeling"),
    ),
    "ACCOUNT_NUMBER_KIND": (
        settings.get("ACCOUNT_NUMBER_KIND", fallback="123"),
        _("Kontostreng art"),
    ),
    "ACCOUNT_NUMBER_UNKNOWN": (
        settings.get("ACCOUNT_NUMBER_UNKNOWN", fallback="UKENDT"),
        _("standardværdi, hvis kontostreng mangler"),
    ),
    "PRISM_ORG_UNIT": (
        settings.get("PRISM_ORG_UNIT", fallback=0),
        _("Kommune-nummer"),
        int,
    ),
    "PRISM_MACHINE_NO": (
        settings.get("PRISM_MACHINE_NO", fallback=0),
        _("Maskin-nummer til PRISME"),
        int,
    ),
}
CONSTANCE_BACKEND = "constance.backends.database.DatabaseBackend"


SBSYS_APPROPRIATION_TEMPLATE = "core/html/appropriation_letter.html"
SBSYS_XML_TEMPLATE = "core/xml/os2forms.xml"

SAML2_AUTH = {
    # Metadata is required, choose either remote url or local
    # file path
    "METADATA_AUTO_CONF_URL": settings.get("SAML_METADATA_URL"),
    "CREATE_USER": "TRUE",
    "NEW_USER_PROFILE": {
        "ACTIVE_STATUS": True,
        "STAFF_STATUS": False,
        "SUPERUSER_STATUS": False,
    },
    "ASSERTION_URL": settings.get("SAML_PUBLIC_HOST"),
    "ENTITY_ID": settings.get("SAML_PUBLIC_HOST"),
    "ATTRIBUTES_MAP": {
        "email": "email",
        "username": "username",
        "first_name": "first_name",
        "last_name": "last_name",
    },
    "TRIGGER": {
        "CREATE_USER": "core.utils.saml_create_user",
        "BEFORE_LOGIN": "core.utils.saml_before_login",
    },
    "USE_JWT": True,
    "FRONTEND_URL": settings.get("SAML_PUBLIC_HOST") + "#/",
    "CERT_FILE": "",
    "KEY_FILE": "",
    "AUTHN_REQUESTS_SIGNED": False,
}

SILENCED_SYSTEM_CHECKS = ["rest_framework.W001"]
