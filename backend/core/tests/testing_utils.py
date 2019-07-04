from decimal import Decimal
from datetime import date

from django.contrib.auth import get_user_model

from core.models import (
    Case,
    Municipality,
    SchoolDistrict,
    Team,
    Activity,
    PaymentSchedule,
    ActivityDetails,
    Appropriation,
    Payment,
    Section,
    SD,
)


User = get_user_model()


class BasicTestMixin:
    @classmethod
    def basic_setup(cls):
        cls.case_worker = User.objects.create(username="Orla Frøsnapper")
        cls.team = Team.objects.create(name="FCK", leader=cls.case_worker)
        cls.municipality = Municipality.objects.create(name="København")
        cls.district = SchoolDistrict.objects.create(name="Baltorpskolen")


def create_case(case_worker, team, municipality, district, sbsys_id="13212"):

    case = Case.objects.create(
        sbsys_id=sbsys_id,
        cpr_number="0205891234",
        name="Jens Jensen",
        case_worker=case_worker,
        team=team,
        scaling_step=1,
        effort_step="STEP_ONE",
        acting_municipality=municipality,
        district=district,
        paying_municipality=municipality,
        residence_municipality=municipality,
    )
    return case


def create_case_as_json(
    case_worker, team, municipality, district, sbsys_id="13212"
):
    json = {
        "sbsys_id": "xxx-yyyx",
        "cpr_number": "111213-0014",
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
):
    payment_schedule = PaymentSchedule.objects.create(
        payment_amount=payment_amount,
        payment_frequency=payment_frequency,
        payment_type=payment_type,
        payment_units=payment_units,
        recipient_type=recipient_type,
        payment_method=payment_method,
    )
    return payment_schedule


def create_activity(
    case,
    appropriation,
    start_date=date(year=2019, month=1, day=1),
    end_date=date(year=2019, month=1, day=10),
    status=Activity.STATUS_DRAFT,
    **kwargs,
):
    activity_details = ActivityDetails.objects.create(
        max_tolerance_in_percent=10, max_tolerance_in_dkk=1000
    )

    activity = Activity.objects.create(
        start_date=start_date,
        end_date=end_date,
        details=activity_details,
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
    payment_schedule = PaymentSchedule.objects.create(
        payment_amount=amount,
        payment_frequency=PaymentSchedule.DAILY,
        payment_type=PaymentSchedule.ONE_TIME_PAYMENT,
        payment_units=0,
    )
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


def create_section(
    paragraph="ABL-105-2",
    kle_number="27.45.04",
    allowed_for_steps=None,
    **kwargs,
):
    if not allowed_for_steps:
        allowed_for_steps = []
    section = Section.objects.create(
        paragraph=paragraph,
        kle_number=kle_number,
        allowed_for_steps=allowed_for_steps,
        **kwargs,
    )
    return section
