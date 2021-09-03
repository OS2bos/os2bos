# Copyright (C) 2019 Magenta ApS, http://magenta.dk.
# Contact: info@magenta.dk.
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
"""Schema models for our graphene API."""

from django.contrib.auth import get_user_model
import graphene
from graphene import Node
from graphene_django_optimizer import OptimizedDjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField

from core.models import (
    Activity as ActivityModel,
    PaymentSchedule as PaymentScheduleModel,
    Payment as PaymentModel,
    ActivityDetails as ActivityDetailsModel,
    ApprovalLevel as ApprovalLevelModel,
    Appropriation as AppropriationModel,
    Case as CaseModel,
    Section as SectionModel,
    Rate as RateModel,
    Price as PriceModel,
)

UserModel = get_user_model()


class User(OptimizedDjangoObjectType):
    """User as a graphene type."""

    pk = graphene.Int(source="pk")

    class Meta:
        model = UserModel
        fields = "__all__"


class ApprovalLevel(OptimizedDjangoObjectType):
    """ApprovalLevel as a graphene type."""

    pk = graphene.Int(source="pk")

    class Meta:
        model = ApprovalLevelModel
        fields = "__all__"


class Case(OptimizedDjangoObjectType):
    """Case as a graphene type."""

    pk = graphene.Int(source="pk")

    class Meta:
        model = CaseModel
        interfaces = (Node,)
        fields = "__all__"
        filter_fields = "__all__"


class Appropriation(OptimizedDjangoObjectType):
    """Appropriation as a graphene type."""

    pk = graphene.Int(source="pk")

    class Meta:
        model = AppropriationModel
        interfaces = (Node,)
        fields = "__all__"
        filter_fields = "__all__"


class Payment(OptimizedDjangoObjectType):
    """Payment as a graphene type."""

    pk = graphene.Int(source="pk")
    account_string = graphene.String()
    account_alias = graphene.String()

    class Meta:
        model = PaymentModel
        interfaces = (Node,)
        fields = "__all__"
        filter_fields = "__all__"


class Rate(OptimizedDjangoObjectType):
    """Rate as a graphene type."""

    pk = graphene.Int(source="pk")

    class Meta:
        model = RateModel
        interfaces = (Node,)
        fields = "__all__"
        filter_fields = "__all__"


class Price(OptimizedDjangoObjectType):
    """Price as a graphene type."""

    pk = graphene.Int(source="pk")

    class Meta:
        model = PriceModel
        interfaces = (Node,)
        fields = "__all__"
        filter_fields = "__all__"


class PaymentSchedule(OptimizedDjangoObjectType):
    """PaymentSchedule as a graphene type."""

    pk = graphene.Int(source="pk")

    class Meta:
        model = PaymentScheduleModel
        interfaces = (Node,)
        fields = "__all__"
        filter_fields = "__all__"


class ActivityDetails(OptimizedDjangoObjectType):
    """ActivityDetails as a graphene type."""

    pk = graphene.Int(source="pk")

    class Meta:
        model = ActivityDetailsModel
        fields = "__all__"


class MonthlyPaymentPlanDictionary(graphene.ObjectType):
    """The monthly payment plan dict on Activity as a custom graphene type."""

    date_month = graphene.String()
    amount = graphene.String()


class Activity(OptimizedDjangoObjectType):
    """Activity as a graphene type."""

    pk = graphene.Int(source="pk")

    total_cost = graphene.Float()
    total_cost_this_year = graphene.Float()
    total_cost_full_year = graphene.Float()
    total_granted_this_year = graphene.Float()
    total_expected_this_year = graphene.Float()
    monthly_payment_plan = graphene.List(MonthlyPaymentPlanDictionary)

    class Meta:
        model = ActivityModel
        interfaces = (Node,)
        fields = "__all__"
        filter_fields = "__all__"


class Section(OptimizedDjangoObjectType):
    """Section as a graphene type."""

    pk = graphene.Int(source="pk")

    class Meta:
        model = SectionModel
        interfaces = (Node,)
        fields = "__all__"
        filter_fields = "__all__"


class Query(graphene.ObjectType):
    """Query define our queryable fields."""

    case = Node.Field(Case)
    cases = DjangoFilterConnectionField(Case)

    activity = Node.Field(Activity)
    activities = DjangoFilterConnectionField(Activity)

    appropriation = Node.Field(Appropriation)
    appropriations = DjangoFilterConnectionField(Appropriation)

    payment_schedule = Node.Field(PaymentSchedule)
    payment_schedules = DjangoFilterConnectionField(PaymentSchedule)

    payment = Node.Field(Payment)
    payments = DjangoFilterConnectionField(Payment)

    rate = Node.Field(Rate)
    rates = DjangoFilterConnectionField(Rate)

    price = Node.Field(Price)
    prices = DjangoFilterConnectionField(Price)

    section = Node.Field(Section)
    sections = DjangoFilterConnectionField(Section)


schema = graphene.Schema(query=Query)
