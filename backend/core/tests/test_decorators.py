from unittest import mock

from django.core.management import call_command
from django.test import TestCase, override_settings

from core.decorators import log_to_prometheus


class TestLogToPrometheus(TestCase):
    @override_settings(LOG_TO_PROMETHEUS=True)
    @mock.patch("core.decorators.pushadd_to_gateway")
    def test_log_to_prometheus_send_expired_emails_success(self, pushadd_mock):
        call_command("send_expired_emails")

        # Assert prometheus is logged to
        self.assertTrue(pushadd_mock.called)
        pushadd_call = pushadd_mock.call_args_list[0]
        self.assertEqual(pushadd_call[1]["job"], "send_expired_emails")

        registry = pushadd_call[1]["registry"]
        # Assert registry for duration gets an appropriate value.
        duration_value = registry.get_sample_value(
            "os2bos_send_expired_emails_duration_seconds"
        )
        self.assertTrue(duration_value > 0)

        # Assert registry for last success gets a value.
        last_success_value = registry.get_sample_value(
            "os2bos_send_expired_emails_last_success"
        )
        breakpoint()
        self.assertTrue(last_success_value > 0)

    @override_settings(LOG_TO_PROMETHEUS=False)
    @mock.patch("core.decorators.pushadd_to_gateway")
    def test_log_to_prometheus_setting_not_set(self, pushadd_mock):
        call_command("send_expired_emails")
        # Assert prometheus is not logged to.
        self.assertFalse(pushadd_mock.called)

    @override_settings(LOG_TO_PROMETHEUS=True)
    @mock.patch("core.decorators.pushadd_to_gateway")
    def test_log_to_prometheus_raised_exception(self, pushadd_mock):
        @log_to_prometheus("raises_exception")
        def raises_exception(self):
            raise Exception

        raises_exception()

        # Assert prometheus is logged to
        self.assertTrue(pushadd_mock.called)
        pushadd_call = pushadd_mock.call_args_list[0]
        self.assertEqual(pushadd_call[1]["job"], "raises_exception")

        # Assert registry for duration gets no value.
        registry = pushadd_call[1]["registry"]
        duration_value = registry.get_sample_value(
            "os2bos_raises_exception_emails_duration_seconds"
        )
        self.assertIsNone(duration_value)

        # Assert registry for last success gets no value.
        last_success_value = registry.get_sample_value(
            "os2bos_raises_exception_last_success"
        )
        self.assertIsNone(last_success_value)
