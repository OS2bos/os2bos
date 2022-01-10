from datetime import date, timedelta
from base64 import b64encode

from django.urls import reverse

from core.models import (
    PaymentSchedule,
    MAIN_ACTIVITY,
    SUPPL_ACTIVITY,
    STATUS_GRANTED,
)
from core.tests.testing_utils import (
    AuthenticatedTestCase,
    BasicTestMixin,
    create_service_provider,
    create_activity_details,
    create_municipality,
    create_case,
    create_appropriation,
    create_payment_schedule,
    create_activity,
    create_payment,
    create_rate,
    create_price,
    create_section,
    create_rate_per_date,
)


class TestExtendedConnection(AuthenticatedTestCase, BasicTestMixin):
    @classmethod
    def setUpTestData(cls):
        cls.basic_setup()

    def test_extended_connection_cases_get(self):
        """the Case model has ExtendedConnection as connection class."""
        reverse_url = reverse("graphql-api")
        self.client.login(username=self.username, password=self.password)
        create_case(self.case_worker, self.municipality, self.district)

        json = {
            "query": """
            query {
                cases {
                    totalCount,
                    edgeCount,
                    edges {
                        node {
                            id,
                        }
                    }
                }
            }"""
        }
        response = self.client.get(reverse_url, json)
        self.assertEqual(response.status_code, 200)
        cases = response.json()["data"]["cases"]

        self.assertEqual(cases["totalCount"], 1)
        self.assertEqual(cases["edgeCount"], 1)


class TestCaseSchema(AuthenticatedTestCase, BasicTestMixin):
    @classmethod
    def setUpTestData(cls):
        cls.basic_setup()

    def test_cases_get(self):
        reverse_url = reverse("graphql-api")
        self.client.login(username=self.username, password=self.password)
        case = create_case(self.case_worker, self.municipality, self.district)

        json = {
            "query": """
            query {
                cases {
                    edges {
                        node {
                            id,
                            name
                        }
                    }
                }
            }"""
        }
        response = self.client.get(reverse_url, json)

        self.assertEqual(response.status_code, 200)
        node = response.json()["data"]["cases"]["edges"][0]["node"]

        self.assertEqual(
            node["id"], b64encode(f"Case:{case.pk}".encode()).decode()
        )
        self.assertEqual(node["name"], case.name)


class TestActivitySchema(AuthenticatedTestCase, BasicTestMixin):
    @classmethod
    def setUpTestData(cls):
        cls.basic_setup()

    def test_activities_get(self):
        reverse_url = reverse("graphql-api")
        self.client.login(username=self.username, password=self.password)

        payment_schedule = create_payment_schedule(
            payment_frequency=PaymentSchedule.DAILY,
            payment_type=PaymentSchedule.RUNNING_PAYMENT,
        )
        case = create_case(self.case_worker, self.municipality, self.district)
        appropriation = create_appropriation(case=case)
        # create a main activity with an expired end_date.
        activity = create_activity(
            case=case,
            appropriation=appropriation,
            payment_plan=payment_schedule,
        )

        json = {
            "query": """
                query {
                    activities {
                        edges {
                            node {
                                id,
                                status,
                                totalGrantedThisYear,
                                totalExpectedThisYear,
                                totalGrantedPreviousYear,
                                totalExpectedPreviousYear,
                                totalGrantedNextYear,
                                totalExpectedNextYear,
                            }
                        }
                    }
                }
            """
        }
        response = self.client.get(reverse_url, json)

        self.assertEqual(response.status_code, 200)

        node = response.json()["data"]["activities"]["edges"][0]["node"]

        self.assertEqual(
            node["id"], b64encode(f"Activity:{activity.pk}".encode()).decode()
        )
        self.assertEqual(node["status"], activity.status)
        self.assertEqual(node["totalGrantedThisYear"], 0.0)
        self.assertEqual(node["totalExpectedThisYear"], 0.0)
        self.assertEqual(node["totalGrantedPreviousYear"], 0.0)
        self.assertEqual(node["totalExpectedPreviousYear"], 0.0)
        self.assertEqual(node["totalGrantedNextYear"], 0.0)
        self.assertEqual(node["totalExpectedNextYear"], 0.0)


class TestActivityDetailsSchema(AuthenticatedTestCase):
    def test_activity_details_get(self):
        reverse_url = reverse("graphql-api")
        self.client.login(username=self.username, password=self.password)

        activity_details = create_activity_details()
        json = {
            "query": """
            query {
                activityDetails {
                    edges {
                        node {
                            id,
                            name
                        }
                    }
                }
            }
            """
        }
        response = self.client.get(reverse_url, json)

        self.assertEqual(response.status_code, 200)
        node = response.json()["data"]["activityDetails"]["edges"][0]["node"]
        self.assertEqual(
            node["id"],
            b64encode(
                f"ActivityDetails:{activity_details.pk}".encode()
            ).decode(),
        )
        self.assertEqual(node["name"], activity_details.name)


class TestAppropriationSchema(AuthenticatedTestCase, BasicTestMixin):
    @classmethod
    def setUpTestData(cls):
        cls.basic_setup()

    def test_appropriations_get(self):
        reverse_url = reverse("graphql-api")
        self.client.login(username=self.username, password=self.password)

        case = create_case(self.case_worker, self.municipality, self.district)
        appropriation = create_appropriation(case)
        json = {
            "query": """
            query {
                appropriations {
                    edges {
                        node {
                            id,
                            sbsysId
                        }
                    }
                }
            }
            """
        }
        response = self.client.get(reverse_url, json)

        self.assertEqual(response.status_code, 200)
        node = response.json()["data"]["appropriations"]["edges"][0]["node"]
        self.assertEqual(
            node["id"],
            b64encode(f"Appropriation:{appropriation.pk}".encode()).decode(),
        )
        self.assertEqual(node["sbsysId"], appropriation.sbsys_id)

    def test_appropriations_get_more_than_100_activities(self):
        reverse_url = reverse("graphql-api")
        self.client.login(username=self.username, password=self.password)
        case = create_case(self.case_worker, self.municipality, self.district)
        appropriation = create_appropriation(case)
        # Create a main activity.
        activity = create_activity(
            case=case,
            appropriation=appropriation,
            activity_type=MAIN_ACTIVITY,
            status=STATUS_GRANTED,
            start_date=date(year=2019, month=12, day=1),
            end_date=date(year=2020, month=2, day=1),
        )
        create_payment_schedule(
            activity=activity, payment_frequency=PaymentSchedule.DAILY
        )
        # Create a whole bunch of supplementary activities.
        for i in range(110):
            activity = create_activity(
                case=case,
                appropriation=appropriation,
                activity_type=SUPPL_ACTIVITY,
                status=STATUS_GRANTED,
                start_date=date(year=2019, month=12, day=1),
                end_date=date(year=2020, month=2, day=1),
            )
            create_payment_schedule(
                activity=activity, payment_frequency=PaymentSchedule.DAILY
            )

        appropriation_id = b64encode(f"Appropriation:{appropriation.pk}".encode()).decode()
        # Assert we can fetch more than the 100 default objects.
        json = {
            "query": f"""
            query {{
                appropriation(id:"{appropriation_id}") {{
                    id,
                    activities {{
                        edges {{
                            node {{
                            id
                            }}
                        }}
                    }}
                }}
            }}
            """
        }
        response = self.client.get(reverse_url, json)
        self.assertEqual(
            len(response.json()["data"]["appropriation"]["activities"]["edges"]),
            111
        )

class TestPaymentScheduleSchema(AuthenticatedTestCase):
    def test_payment_schedules_get(self):
        reverse_url = reverse("graphql-api")
        self.client.login(username=self.username, password=self.password)

        payment_schedule = create_payment_schedule(
            payment_frequency=PaymentSchedule.DAILY,
            payment_type=PaymentSchedule.RUNNING_PAYMENT,
        )

        json = {
            "query": """
            query {
                paymentSchedules {
                    edges {
                        node {
                            id,
                            paymentFrequency
                        }
                    }
                }
            }
            """
        }
        response = self.client.get(reverse_url, json)

        self.assertEqual(response.status_code, 200)
        node = response.json()["data"]["paymentSchedules"]["edges"][0]["node"]
        self.assertEqual(
            node["id"],
            b64encode(
                f"PaymentSchedule:{payment_schedule.pk}".encode()
            ).decode(),
        )
        self.assertEqual(
            node["paymentFrequency"], payment_schedule.payment_frequency
        )


class TestPaymentSchema(AuthenticatedTestCase):
    def test_payments_get(self):
        reverse_url = reverse("graphql-api")
        self.client.login(username=self.username, password=self.password)

        payment_schedule = create_payment_schedule()
        payment = create_payment(payment_schedule)

        json = {
            "query": """
            query {
                payments {
                    edges {
                        node {
                            id,
                            date,
                            amount,
                            accountString,
                            accountAlias,
                            isPayableManually,
                        }
                    }
                }
            }
            """
        }
        response = self.client.get(reverse_url, json)

        self.assertEqual(response.status_code, 200)
        node = response.json()["data"]["payments"]["edges"][0]["node"]
        self.assertEqual(
            node["id"],
            b64encode(f"Payment:{payment.pk}".encode()).decode(),
        )
        self.assertEqual(node["date"], str(payment.date))
        self.assertEqual(node["amount"], "500.00")


class TestRateSchema(AuthenticatedTestCase):
    def test_rates_get(self):
        reverse_url = reverse("graphql-api")
        self.client.login(username=self.username, password=self.password)

        rate = create_rate()

        json = {
            "query": """
            query {
                rates {
                    edges {
                        node {
                            id,
                            name,
                        }
                    }
                }
            }
            """
        }
        response = self.client.get(reverse_url, json)

        self.assertEqual(response.status_code, 200)
        node = response.json()["data"]["rates"]["edges"][0]["node"]
        self.assertEqual(
            node["id"],
            b64encode(f"Rate:{rate.pk}".encode()).decode(),
        )
        self.assertEqual(node["name"], rate.name)


class TestPriceSchema(AuthenticatedTestCase):
    def test_prices_get(self):
        reverse_url = reverse("graphql-api")
        self.client.login(username=self.username, password=self.password)

        payment_schedule = create_payment_schedule()
        price = create_price(payment_schedule)

        json = {
            "query": """
            query {
                prices {
                    edges {
                        node {
                            id,
                            paymentSchedule {
                                id
                            }
                        }
                    }
                }
            }
            """
        }
        response = self.client.get(reverse_url, json)
        self.assertEqual(response.status_code, 200)
        node = response.json()["data"]["prices"]["edges"][0]["node"]
        self.assertEqual(
            node["id"],
            b64encode(f"Price:{price.pk}".encode()).decode(),
        )
        self.assertEqual(
            node["paymentSchedule"]["id"],
            b64encode(
                f"PaymentSchedule:{payment_schedule.pk}".encode()
            ).decode(),
        )


class TestSectionSchema(AuthenticatedTestCase):
    def test_sections_get(self):
        reverse_url = reverse("graphql-api")
        self.client.login(username=self.username, password=self.password)

        section = create_section()

        json = {
            "query": """
            query {
                sections {
                    edges {
                        node {
                            id,
                            paragraph,

                        }
                    }
                }
            }
            """
        }
        response = self.client.get(reverse_url, json)
        self.assertEqual(response.status_code, 200)
        node = response.json()["data"]["sections"]["edges"][0]["node"]
        self.assertEqual(
            node["id"],
            b64encode(f"Section:{section.pk}".encode()).decode(),
        )
        self.assertEqual(
            node["paragraph"],
            section.paragraph,
        )


class TestRatePerDateSchema(AuthenticatedTestCase):
    def test_rate_per_dates_get(self):
        reverse_url = reverse("graphql-api")
        self.client.login(username=self.username, password=self.password)

        rate = create_rate(name="test rate")
        today = date.today()
        tomorrow = date.today() + timedelta(days=1)
        rate_per_date = create_rate_per_date(
            rate, rate=100, start_date=today, end_date=tomorrow
        )

        json = {
            "query": """
            query {
                ratePerDates {
                    edges {
                        node {
                            id,
                            rate,
                            startDate,
                            endDate,

                        }
                    }
                }
            }
            """
        }
        response = self.client.get(reverse_url, json)
        self.assertEqual(response.status_code, 200)
        node = response.json()["data"]["ratePerDates"]["edges"][0]["node"]
        self.assertEqual(
            node["id"],
            b64encode(f"RatePerDate:{rate_per_date.pk}".encode()).decode(),
        )
        self.assertEqual(node["rate"], "100.00")
        self.assertEqual(node["startDate"], str(rate_per_date.start_date))
        self.assertEqual(node["endDate"], str(rate_per_date.end_date))


class TestServiceProviderSchema(AuthenticatedTestCase):
    def test_service_providers_get(self):
        reverse_url = reverse("graphql-api")
        self.client.login(username=self.username, password=self.password)

        service_provider = create_service_provider()
        json = {
            "query": """
            query {
                serviceProviders {
                    edges {
                        node {
                            id,
                            name
                        }
                    }
                }
            }
            """
        }
        response = self.client.get(reverse_url, json)

        self.assertEqual(response.status_code, 200)
        node = response.json()["data"]["serviceProviders"]["edges"][0]["node"]
        self.assertEqual(
            node["id"],
            b64encode(
                f"ServiceProvider:{service_provider.pk}".encode()
            ).decode(),
        )
        self.assertEqual(node["name"], "MAGENTA ApS")


class TestMunicipalitySchema(AuthenticatedTestCase):
    def test_municipalities_get(self):
        reverse_url = reverse("graphql-api")
        self.client.login(username=self.username, password=self.password)

        municipality = create_municipality()
        json = {
            "query": """
                query {
                    municipalities {
                        edges {
                            node {
                                id,
                                name
                            }
                        }
                    }
                }
            """
        }
        response = self.client.get(reverse_url, json)

        self.assertEqual(response.status_code, 200)

        node = response.json()["data"]["municipalities"]["edges"][0]["node"]
        self.assertEqual(
            node["id"],
            b64encode(f"Municipality:{municipality.pk}".encode()).decode(),
        )
        self.assertEqual(node["name"], "København")
