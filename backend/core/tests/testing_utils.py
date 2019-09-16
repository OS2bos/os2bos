# Copyright (C) 2019 Magenta ApS, http://magenta.dk.
# Contact: info@magenta.dk.
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.


from decimal import Decimal
from datetime import date

from django.contrib.auth import get_user_model
from django.test import TestCase

from core.models import (
    Case,
    Municipality,
    SchoolDistrict,
    Team,
    Activity,
    STATUS_DRAFT,
    PaymentSchedule,
    ActivityDetails,
    Appropriation,
    Payment,
    ServiceProvider,
    Section,
    Account,
    SD,
    FAMILY_DEPT,
)


User = get_user_model()


class AuthenticatedTestCase(TestCase):
    """Simple class for authenticating before accessing a view."""

    def setUp(self):
        self.username = "user"
        self.password = "s1kr3t"
        self.user = User.objects.create_user(
            self.username, f"{self.username}@company.com", self.password
        )


class BasicTestMixin:
    @classmethod
    def basic_setup(cls):
        cls.case_worker = User.objects.create(username="Orla Frøsnapper")
        cls.team = Team.objects.create(name="FCK", leader=cls.case_worker)
        cls.municipality = Municipality.objects.create(name="København")
        cls.district = SchoolDistrict.objects.create(name="Baltorpskolen")


def create_case(
    case_worker,
    team,
    municipality,
    district,
    sbsys_id="13212",
    scaling_step=1,
    effort_step="STEP_ONE",
    target_group=FAMILY_DEPT,
):

    case = Case.objects.create(
        sbsys_id=sbsys_id,
        cpr_number="0205891234",
        name="Jens Jensen",
        case_worker=case_worker,
        team=team,
        scaling_step=scaling_step,
        effort_step=effort_step,
        acting_municipality=municipality,
        district=district,
        paying_municipality=municipality,
        residence_municipality=municipality,
        target_group=target_group,
    )
    return case


def create_case_as_json(
    case_worker, team, municipality, district, sbsys_id="13212"
):
    json = {
        "sbsys_id": "xxx-yyyx",
        "cpr_number": "1112130014",
        "name": "Mak Mouse",
        "target_group": "FAMILY_DEPT",
        "refugee_integration": True,
        "cross_department_measure": True,
        "case_worker": case_worker.id,
        "team": team.id,
        "scaling_step": 1,
        "effort_step": "STEP_ONE",
        "district": district.id,
        "paying_municipality": municipality.id,
        "acting_municipality": municipality.id,
        "residence_municipality": municipality.id,
    }

    return json


def create_payment_schedule(
    payment_frequency=PaymentSchedule.DAILY,
    payment_type=PaymentSchedule.RUNNING_PAYMENT,
    payment_amount=Decimal("500.0"),
    payment_units=0,
    recipient_type=PaymentSchedule.PERSON,
    payment_method=SD,
    recipient_id="0205891234",
    recipient_name="Jens Testersen",
    payment_day_of_month=1,
):
    payment_schedule = PaymentSchedule.objects.create(
        payment_amount=payment_amount,
        payment_frequency=payment_frequency,
        payment_type=payment_type,
        payment_units=payment_units,
        recipient_type=recipient_type,
        payment_method=payment_method,
        recipient_id=recipient_id,
        recipient_name=recipient_name,
        payment_day_of_month=payment_day_of_month,
    )
    return payment_schedule


def create_activity(
    case,
    appropriation,
    start_date=date(year=2019, month=1, day=1),
    end_date=date(year=2019, month=1, day=10),
    status=STATUS_DRAFT,
    **kwargs,
):
    if "details" not in kwargs:
        details, unused = ActivityDetails.objects.get_or_create(
            activity_id="000000",
            name="Test aktivitet",
            max_tolerance_in_percent=10,
            max_tolerance_in_dkk=1000,
        )
    else:
        details = kwargs.pop("details")

    activity = Activity.objects.create(
        start_date=start_date,
        end_date=end_date,
        details=details,
        status=status,
        appropriation=appropriation,
        **kwargs,
    )
    return activity


def create_appropriation(case, sbsys_id="13212", **kwargs):
    appropriation = Appropriation.objects.create(
        sbsys_id=sbsys_id, case=case, **kwargs
    )
    return appropriation


def create_payment(
    payment_schedule,
    date=date.today(),
    amount=Decimal("500"),
    recipient_type=PaymentSchedule.PERSON,
    payment_method=SD,
):
    payment = Payment.objects.create(
        recipient_id="Test",
        recipient_name="Test",
        recipient_type=recipient_type,
        payment_method=payment_method,
        date=date,
        amount=amount,
        payment_schedule=payment_schedule,
    )
    return payment


def create_section(paragraph="ABL-105-2", allowed_for_steps=None, **kwargs):
    if not allowed_for_steps:
        allowed_for_steps = []
    section = Section.objects.create(
        paragraph=paragraph, allowed_for_steps=allowed_for_steps, **kwargs
    )
    return section


def create_account(
    main_activity, supplementary_activity, section, number="12345678"
):
    account = Account.objects.create(
        main_activity=main_activity,
        supplementary_activity=supplementary_activity,
        section=section,
        number=number,
    )
    return account


def create_service_provider(cvr_number, name):
    service_provider = ServiceProvider.objects.create(
        cvr_number=cvr_number, name=name
    )

    return service_provider
