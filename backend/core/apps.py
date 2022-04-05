# Copyright (C) 2019 Magenta ApS, http://magenta.dk.
# Contact: info@magenta.dk.
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
"""Core app configuration."""

from django.apps import AppConfig


class CoreConfig(AppConfig):
    """The core Django app."""

    name = "core"

    def ready(self):
        """Defer import of signals until ready."""
        import core.signals  # noqa


class ModifiedConstanceDatabaseConfig(AppConfig):
    """Modified django-constance AppConfig.

    While we wait for django-constance to provide their
    own apps.py specifying default_auto_field:
    https://github.com/jazzband/django-constance/pull/449
    """

    name = "constance.backends.database"
    default_auto_field = "django.db.models.AutoField"
