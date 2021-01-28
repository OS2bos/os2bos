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

from django_currentuser.middleware import _set_current_user

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
    SectionInfo,
    RelatedPerson,
    SD,
    EffortStep,
    TargetGroup,
    VariableRate,
    Rate,
    RatePerDate,
    PaymentDateExclusion,
    AccountAlias,
    AccountAliasMapping,
    ActivityCategory,
)


User = get_user_model()


class AuthenticatedTestCase(TestCase):
    """Simple class for authenticating before accessing a view."""

    def setUp(self):
        self.username = "user"
        self.password = "s1kr3t"
        self.user = User.objects.create_user(
            self.username,
            f"{self.username}@company.com",
            self.password,
            profile="grant",
        )


class BasicTestMixin:
    @classmethod
    def basic_setup(cls):
        cls.case_worker, _ = User.objects.get_or_create(
            username="Orla Frøsnapper",
        )
        _set_current_user(cls.case_worker)
        cls.team, _ = Team.objects.get_or_create(
            name="FCK", leader=cls.case_worker
        )
        cls.case_worker.team = cls.team
        cls.case_worker.save()
        cls.municipality, _ = Municipality.objects.get_or_create(
            name="København"
        )
        cls.district, _ = SchoolDistrict.objects.get_or_create(
            name="Baltorpskolen"
        )


def create_case(
    case_worker,
    municipality,
    district,
    sbsys_id="13212",
    scaling_step=1,
    effort_step=1,
    target_group="Familieafdelingen",
    cpr_number="0205891234",
):
    target_group = TargetGroup.objects.get(name=target_group)
    effort_step = EffortStep.objects.get(number=effort_step)

    case = Case.objects.create(
        sbsys_id=sbsys_id,
        cpr_number=cpr_number,
        name="Jens Jensen",
        case_worker=case_worker,
        scaling_step=scaling_step,
        effort_step=effort_step,
        acting_municipality=municipality,
        district=district,
        paying_municipality=municipality,
        residence_municipality=municipality,
        target_group=target_group,
    )
    return case


def create_case_as_json(case_worker, municipality, district, sbsys_id="13212"):
    json = {
        "sbsys_id": "xxx-yyyx",
        "cpr_number": "1112130014",
        "name": "Mak Mouse",
        "target_group": 1,
        "refugee_integration": True,
        "cross_department_measure": True,
        "case_worker": case_worker.id,
        "scaling_step": 1,
        "effort_step": 1,
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
    payment_cost_type=PaymentSchedule.FIXED_PRICE,
    fictive=False,
    **kwargs,
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
        fictive=fictive,
        payment_cost_type=payment_cost_type,
        **kwargs,
    )
    return payment_schedule


def create_activity_details(
    activity_id="000000",
    name="Test aktivitet",
    max_tolerance_in_percent=10,
    max_tolerance_in_dkk=1000,
):
    details, unused = ActivityDetails.objects.get_or_create(
        activity_id=activity_id,
        name=name,
        max_tolerance_in_percent=max_tolerance_in_percent,
        max_tolerance_in_dkk=max_tolerance_in_dkk,
    )
    return details


def create_activity(
    case,
    appropriation,
    start_date=date(year=2019, month=1, day=1),
    end_date=date(year=2019, month=1, day=10),
    status=STATUS_DRAFT,
    **kwargs,
):
    if "details" not in kwargs:
        details = create_activity_details()
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
    saved_account_string="",
    paid_amount=None,
    paid_date=None,
    paid=False,
):
    payment = Payment.objects.create(
        recipient_id="Test",
        recipient_name="Test",
        recipient_type=recipient_type,
        payment_method=payment_method,
        date=date,
        amount=amount,
        payment_schedule=payment_schedule,
        saved_account_string=saved_account_string,
        paid_amount=paid_amount,
        paid_date=paid_date,
        paid=paid,
    )
    return payment


def create_section(paragraph="ABL-105-2", allowed_for_steps=None, **kwargs):
    if not allowed_for_steps:
        allowed_for_steps = []
    section = Section.objects.create(paragraph=paragraph, **kwargs)
    for step in allowed_for_steps:
        section.allowed_for_steps.add(EffortStep.objects.get(number=step))
    return section


def create_service_provider(cvr_number, name):
    service_provider = ServiceProvider.objects.create(
        cvr_number=cvr_number, name=name
    )

    return service_provider


def create_section_info(
    details,
    section,
    kle_number="27.18.02",
    sbsys_template_id="900",
    main_activity_main_account_number="1234",
    supplementary_activity_main_account_number="5678",
):
    params = {
        "activity_details": details,
        "section": section,
        "kle_number": kle_number,
        "sbsys_template_id": sbsys_template_id,
        "main_activity_main_account_number": main_activity_main_account_number,
        "supplementary_activity_"
        "main_account_number": supplementary_activity_main_account_number,
    }

    section_info = SectionInfo.objects.create(**params)
    return section_info


def create_related_person(
    main_case, name="Jens Jensen", relation_type="far", cpr_number="0000000000"
):
    related_person = RelatedPerson.objects.create(
        main_case=main_case,
        name=name,
        relation_type=relation_type,
        cpr_number=cpr_number,
    )
    return related_person


def create_user(username):
    user = User.objects.create(username=username)
    return user


def create_target_group(
    name="Familieafdelingen", required_fields_for_case=None
):
    if required_fields_for_case is None:
        required_fields_for_case = "district"
    target_group, _ = TargetGroup.objects.get_or_create(
        name=name, required_fields_for_case=required_fields_for_case
    )
    return target_group


def create_effort_step(name="Trin 1: Tidlig indsats i almenområdet", number=1):
    effort_step, _ = EffortStep.objects.get_or_create(
        number=number, defaults={"name": name}
    )

    return effort_step


def create_variable_rate():
    variable_rate, _ = VariableRate.objects.get_or_create()
    return variable_rate


def create_rate(name="Test rate", description="test description"):
    rate, _ = Rate.objects.get_or_create(name=name, description=description)
    return rate


def create_rate_per_date(main_rate, rate=100, start_date=None, end_date=None):
    rate_per_date, _ = RatePerDate.objects.get_or_create(
        main_rate=main_rate,
        rate=rate,
        start_date=start_date,
        end_date=end_date,
    )
    return rate_per_date


def create_payment_date_exclusion(date=date.today()):
    payment_date_exclusion, _ = PaymentDateExclusion.objects.get_or_create(
        date=date
    )

    return payment_date_exclusion


def create_account_alias(section_info, activity_details, alias="BOS0000001"):
    account_alias, _ = AccountAlias.objects.get_or_create(
        section_info=section_info,
        activity_details=activity_details,
        alias=alias,
    )

    return account_alias


def create_account_alias_mapping(
    main_account_number, activity_number, alias="BOS0000001"
):
    account_alias_mapping, _ = AccountAliasMapping.objects.get_or_create(
        main_account_number=main_account_number,
        activity_number=activity_number,
        alias=alias,
    )

    return account_alias_mapping


def create_activity_category(
    category_id="123456", name="test aktivitetskategori"
):
    activity_category, _ = ActivityCategory.objects.get_or_create(
        category_id=category_id, name=name
    )

    return activity_category
