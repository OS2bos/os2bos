from django.contrib.auth import get_user_model
from graphene_django import DjangoObjectType
import graphene
from graphene import Node
from graphene.types.generic import GenericScalar
from graphene_django_optimizer import OptimizedDjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField

import django_filters

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
    Price as PriceModel
)

UserModel = get_user_model()


class User(OptimizedDjangoObjectType):
    pk = graphene.Int(source="pk")

    class Meta:
        model = UserModel
        fields = "__all__"


class ApprovalLevel(OptimizedDjangoObjectType):
    pk = graphene.Int(source="pk")
    
    class Meta:
        model = ApprovalLevelModel
        fields = "__all__"


class Case(OptimizedDjangoObjectType):
    pk = graphene.Int(source="pk")

    class Meta:
        model = CaseModel
        interfaces = (Node,)
        fields = "__all__"
        filter_fields = "__all__"


class Appropriation(OptimizedDjangoObjectType):
    pk = graphene.Int(source="pk")

    class Meta:
        model = AppropriationModel
        interfaces = (Node,)
        fields = "__all__"
        filter_fields = "__all__"


class Payment(OptimizedDjangoObjectType):
    pk = graphene.Int(source="pk")
    account_string = graphene.String()
    account_alias = graphene.String()

    class Meta:
        model = PaymentModel
        interfaces = (Node,)
        fields = "__all__"
        filter_fields = "__all__"


class Rate(OptimizedDjangoObjectType):

    class Meta:
        model = RateModel
        interfaces = (Node,)
        fields = "__all__"
        filter_fields = "__all__"


class Price(OptimizedDjangoObjectType):

    class Meta:
        model = PriceModel
        interfaces = (Node,)
        fields = "__all__"
        filter_fields = "__all__"


class PaymentSchedule(OptimizedDjangoObjectType):
    pk = graphene.Int(source="pk")

    class Meta:
        model = PaymentScheduleModel
        interfaces = (Node,)
        fields = "__all__"
        filter_fields = "__all__"


class ActivityDetails(OptimizedDjangoObjectType):
    pk = graphene.Int(source="pk")

    class Meta:
        model = ActivityDetailsModel
        fields = "__all__"


class MonthlyPaymentPlanDictionary(graphene.ObjectType):
    date_month = graphene.String()
    amount = graphene.String()


class Activity(OptimizedDjangoObjectType):
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
    pk = graphene.Int(source="pk")

    class Meta:
        model = SectionModel
        interfaces = (Node,)
        fields = "__all__"
        filter_fields = "__all__"


class Query(graphene.ObjectType):
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
