from django.test import TestCase

from core.tests.testing_utils import (
    BasicTestMixin,
    create_section,
    create_effort_step,
    create_activity_details,
    create_rate,
    create_rate_per_date,
)

from core.proxies import (
    SectionEffortStepProxy,
    ActivityDetailsSectionProxy,
    HistoricalRatePerDateProxy,
)


class SectionEffortStepProxyTestCase(TestCase):
    def test_section_effort_step_proxy_str(self):
        section = create_section(text="test beskrivelse")
        effort_step = create_effort_step()
        section.allowed_for_steps.add(effort_step)

        section_effort_step_proxy = SectionEffortStepProxy.objects.first()
        self.assertEqual(
            str(section_effort_step_proxy), "ABL-105-2 test beskrivelse"
        )


class ActivityDetailsSectionProxyTestCase(TestCase):
    def test_activity_details_section_proxy_str(self):
        activity_details = create_activity_details()
        section = create_section()
        activity_details.supplementary_activity_for.add(section)

        activity_details_section_proxy = (
            ActivityDetailsSectionProxy.objects.first()
        )
        self.assertEqual(
            str(activity_details_section_proxy),
            "000000 - Test aktivitet - ABL-105-2",
        )


class HistoricalRatePerDateProxyTestCase(TestCase, BasicTestMixin):
    @classmethod
    def setUpTestData(cls):
        cls.basic_setup()

    def test_historical_rate_per_date_proxy_str(self):
        rate = create_rate()
        create_rate_per_date(rate)

        historical_rate_per_date_proxy = (
            HistoricalRatePerDateProxy.objects.first()
        )
        self.assertEqual(
            str(historical_rate_per_date_proxy), "100.00 - None - None"
        )
