# -*- coding: utf-8 -*-
from datetime import timedelta
from django.test import TestCase
from django.utils import timezone
from django.core import mail
from parameterized import parameterized

from core.models import (
    Municipality,
    SchoolDistrict,
    Sections,
    ActivityCatalog,
    Payment,
    PaymentSchedule,
    FAMILY_DEPT,
)


class MunicipalityTestCase(TestCase):
    def test_municipality_str(self):
        municipality = Municipality.objects.create(name="København")

        self.assertEqual(str(municipality), "København")


class SchoolDistrictTestCase(TestCase):
    def test_school_district_str(self):
        school_district = SchoolDistrict.objects.create(name="Skovlunde Skole")

        self.assertEqual(str(school_district), "Skovlunde Skole")


class SectionsTestCase(TestCase):
    def test_sections_str(self):
        sections = Sections.objects.create(
            paragraph="ABL-105-2",
            kle_number="27.45.04",
            text="Lov om almene boliger",
            allowed_for_steps=[],
            target_group=FAMILY_DEPT,
            law_text_name="Lov om almene boliger",
        )

        self.assertEqual(str(sections), "ABL-105-2 - 27.45.04")


class ActivityCatalogTestCase(TestCase):
    def test_activitycatalog_str(self):
        catalog = ActivityCatalog.objects.create(
            name="Betaling til andre kommuner/region for specialtandpleje",
            activity_id="010001",
            max_tolerance_in_dkk=5000,
            max_tolerance_in_percent=10,
        )

        self.assertEqual(
            str(catalog),
            "010001 - Betaling til andre kommuner/region for specialtandpleje",
        )


class PaymentTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.payment_schedule = PaymentSchedule.objects.create()

    @parameterized.expand(
        [
            (PaymentSchedule.PERSON, PaymentSchedule.SD),
            (PaymentSchedule.PERSON, PaymentSchedule.CASH),
            (PaymentSchedule.INTERNAL, PaymentSchedule.INTERNAL),
            (PaymentSchedule.COMPANY, PaymentSchedule.INVOICE),
        ]
    )
    def test_payment_and_recipient_allowed_save(
        self, recipient_type, payment_method
    ):
        payment = Payment.objects.create(
            payment_schedule=self.payment_schedule,
            date=timezone.now(),
            recipient_type=recipient_type,
            payment_method=payment_method,
        )
        self.assertEqual(payment.recipient_type, recipient_type)
        self.assertEqual(payment.payment_method, payment_method)

    @parameterized.expand(
        [
            (PaymentSchedule.PERSON, PaymentSchedule.INTERNAL),
            (PaymentSchedule.PERSON, PaymentSchedule.INVOICE),
            (PaymentSchedule.INTERNAL, PaymentSchedule.CASH),
            (PaymentSchedule.INTERNAL, PaymentSchedule.SD),
            (PaymentSchedule.INTERNAL, PaymentSchedule.INVOICE),
            (PaymentSchedule.COMPANY, PaymentSchedule.INTERNAL),
            (PaymentSchedule.COMPANY, PaymentSchedule.SD),
            (PaymentSchedule.COMPANY, PaymentSchedule.CASH),
        ]
    )
    def test_payment_and_recipient_disallowed_save(
        self, recipient_type, payment_method
    ):
        with self.assertRaises(ValueError):
            Payment.objects.create(
                payment_schedule=self.payment_schedule,
                date=timezone.now(),
                recipient_type=recipient_type,
                payment_method=payment_method,
            )

    def test_payment_create_email_sent(self):
        # Should trigger a create email.
        Payment.objects.create(
            payment_schedule=self.payment_schedule,
            date=timezone.now(),
            recipient_type=PaymentSchedule.PERSON,
            payment_method=PaymentSchedule.SD,
        )
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, "Betaling oprettet")

    def test_payment_update_email_sent(self):
        payment = Payment.objects.create(
            payment_schedule=self.payment_schedule,
            date=timezone.now(),
            recipient_type=PaymentSchedule.PERSON,
            payment_method=PaymentSchedule.SD,
        )
        # Should trigger a update email.
        payment.date = timezone.now() + timedelta(days=3)
        payment.save()
        self.assertEqual(len(mail.outbox), 2)
        self.assertEqual(mail.outbox[1].subject, "Betaling ændret")

    def test_payment_delete_email_sent(self):
        payment = Payment.objects.create(
            payment_schedule=self.payment_schedule,
            date=timezone.now(),
            recipient_type=PaymentSchedule.PERSON,
            payment_method=PaymentSchedule.SD,
        )
        # Should trigger a delete mail.
        payment.delete()
        self.assertEqual(len(mail.outbox), 2)
        self.assertEqual(mail.outbox[1].subject, "Betaling slettet")

    def test_payment_create_email_shouldnt_send(self):
        Payment.objects.create(
            payment_schedule=self.payment_schedule,
            date=timezone.now(),
            recipient_type=PaymentSchedule.PERSON,
            payment_method=PaymentSchedule.CASH,
        )
        # Shouldn't trigger an email.
        self.assertEqual(len(mail.outbox), 0)

    def test_payment_delete_email_shouldnt_send(self):
        payment = Payment.objects.create(
            payment_schedule=self.payment_schedule,
            date=timezone.now(),
            recipient_type=PaymentSchedule.PERSON,
            payment_method=PaymentSchedule.CASH,
        )
        payment.delete()
        # Shouldn't trigger an email.
        self.assertEqual(len(mail.outbox), 0)
