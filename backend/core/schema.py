# Copyright (C) 2019 Magenta ApS, http://magenta.dk.
# Contact: info@magenta.dk.
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
"""Schema models for our graphene API."""

from django.contrib.auth import get_user_model
from django.utils import timezone

import graphene
from graphene import Node, Connection
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
    RatePerDate as RatePerDateModel,
)

UserModel = get_user_model()


class ExtendedConnection(Connection):
    class Meta:
        abstract = True

    total_count = graphene.Int()
    edge_count = graphene.Int()

    def resolve_total_count(root, info, **kwargs):
        return root.length

    def resolve_edge_count(root, info, **kwargs):
        return len(root.edges)


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
        connection_class = ExtendedConnection
        fields = "__all__"
        filter_fields = "__all__"


class Appropriation(OptimizedDjangoObjectType):
    """Appropriation as a graphene type."""

    pk = graphene.Int(source="pk")

    class Meta:
        model = AppropriationModel
        interfaces = (Node,)
        connection_class = ExtendedConnection
        fields = "__all__"
        filter_fields = "__all__"


class Payment(OptimizedDjangoObjectType):
    """Payment as a graphene type."""

    pk = graphene.Int(source="pk")
    account_string = graphene.String()
    account_alias = graphene.String()
    is_payable_manually = graphene.Boolean()

    class Meta:
        model = PaymentModel
        interfaces = (Node,)
        connection_class = ExtendedConnection
        fields = "__all__"
        filter_fields = "__all__"


class Rate(OptimizedDjangoObjectType):
    """Rate as a graphene type."""

    pk = graphene.Int(source="pk")

    class Meta:
        model = RateModel
        interfaces = (Node,)
        connection_class = ExtendedConnection
        fields = "__all__"
        filter_fields = "__all__"


class Price(OptimizedDjangoObjectType):
    """Price as a graphene type."""

    pk = graphene.Int(source="pk")
    current_amount = graphene.Decimal(source="rate_amount")

    class Meta:
        model = PriceModel
        interfaces = (Node,)
        connection_class = ExtendedConnection
        fields = "__all__"
        filter_fields = "__all__"


class RatePerDate(OptimizedDjangoObjectType):
    """RatePerDate as a graphene type."""

    pk = graphene.Int(source="pk")

    class Meta:
        model = RatePerDateModel
        interfaces = (Node,)
        connection_class = ExtendedConnection
        fields = "__all__"
        filter_fields = "__all__"


class PaymentSchedule(OptimizedDjangoObjectType):
    """PaymentSchedule as a graphene type."""

    pk = graphene.Int(source="pk")
    can_be_paid = graphene.Boolean()

    class Meta:
        model = PaymentScheduleModel
        interfaces = (Node,)
        connection_class = ExtendedConnection
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

    total_granted_this_year = graphene.Float()
    total_expected_this_year = graphene.Float()

    total_granted_previous_year = graphene.Float()
    total_expected_previous_year = graphene.Float()

    total_granted_next_year = graphene.Float()
    total_expected_next_year = graphene.Float()

    def resolve_total_granted_this_year(self, info):
        """Retrieve total granted amount for this year."""
        year = timezone.now().year

        return self.total_granted_in_year(year)

    def resolve_total_expected_this_year(self, info):
        """Retrieve total expected amount for this year."""
        year = timezone.now().year

        return self.total_expected_in_year(year)

    def resolve_total_granted_previous_year(self, info):
        """Retrieve total granted amount for previous year."""
        year = timezone.now().year - 1

        return self.total_granted_in_year(year)

    def resolve_total_expected_previous_year(self, info):
        """Retrieve total expected amount for previous year."""
        year = timezone.now().year - 1

        return self.total_expected_in_year(year)

    def resolve_total_granted_next_year(self, info):
        """Retrieve total granted amount for next year."""
        year = timezone.now().year + 1

        return self.total_granted_in_year(year)

    def resolve_total_expected_next_year(self, info):
        """Retrieve total expected amount for next year."""
        year = timezone.now().year + 1

        return self.total_expected_in_year(year)

    class Meta:
        model = ActivityModel
        interfaces = (Node,)
        connection_class = ExtendedConnection
        fields = "__all__"
        filter_fields = "__all__"


class Section(OptimizedDjangoObjectType):
    """Section as a graphene type."""

    pk = graphene.Int(source="pk")

    class Meta:
        model = SectionModel
        interfaces = (Node,)
        connection_class = ExtendedConnection
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

    rate_per_date = Node.Field(RatePerDate)
    rate_per_dates = DjangoFilterConnectionField(RatePerDate)


schema = graphene.Schema(query=Query)
