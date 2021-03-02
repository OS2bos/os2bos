# Copyright (C) 2019 Magenta ApS, http://magenta.dk.
# Contact: info@magenta.dk.
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
"""Decorators used by other parts of this app."""
from django.conf import settings

from prometheus_client import Gauge, CollectorRegistry, pushadd_to_gateway


def log_to_prometheus(job_name):
    """
    Log function metrics to prometheus.

    for example @log_to_prometheus('send_expired_emails')
    """

    def decorator_log_to_prometheus(job_func):
        def wrapper_log_to_prometheus(*args, **kwargs):
            result = None
            if not settings.PUSHGATEWAY_HOST:
                result = job_func(*args, **kwargs)
            else:
                registry = CollectorRegistry()
                duration = Gauge(
                    f"os2bos_{job_name}_duration_seconds",
                    f"Duration of {job_name}",
                    registry=registry,
                )

                try:
                    with duration.time():
                        result = job_func(*args, **kwargs)
                except Exception:
                    pass
                else:
                    # only runs when there are no exceptions
                    last_success = Gauge(
                        f"os2bos_{job_name}_last_success",
                        f"Unixtime {job_name} last succeeded",
                        registry=registry,
                    )
                    last_success.set_to_current_time()
                finally:
                    pushadd_to_gateway(
                        settings.PUSHGATEWAY_HOST,
                        job=f"{job_name}",
                        registry=registry,
                    )
            return result

        return wrapper_log_to_prometheus

    return decorator_log_to_prometheus
