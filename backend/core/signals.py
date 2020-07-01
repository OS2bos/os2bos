# Copyright (C) 2019 Magenta ApS, http://magenta.dk.
# Contact: info@magenta.dk.
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
"""Signals for acting on events occuring on model objects."""

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from core.models import (
    Activity,
    PaymentSchedule,
    Price,
    Rate,
    Payment,
    STATUS_EXPECTED,
    STATUS_DRAFT,
)
from core.utils import (
    send_activity_created_email,
    send_activity_updated_email,
    send_activity_deleted_email,
)


@receiver(
    post_save,
    sender=Payment,
    dispatch_uid="set_saved_account_string_on_payment_save",
)
def set_saved_account_string_on_payment_save(
    sender, instance, created, **kwargs
):
    """Set the saved_account_string on Payment save."""
    if (
        instance.paid
        and not instance.saved_account_string
        and instance.account_string
    ):
        instance.saved_account_string = instance.account_string
        instance.save()


@receiver(
    post_save,
    sender=PaymentSchedule,
    dispatch_uid="set_payment_id_on_paymentschedule_save",
)
def set_payment_id_on_paymentschedule_save(
    sender, instance, created, **kwargs
):
    """Set the payment_id as the PaymentSchedule ID on creation."""
    if created:
        instance.payment_id = instance.id
        instance.save()


@receiver(
    post_save,
    sender=PaymentSchedule,
    dispatch_uid="send_activity_created_email_on_paymentschedule_create",
)
def send_activity_created_email_on_paymentschedule_create(
    sender, instance, created, **kwargs
):
    """Set the payment_id as the PaymentSchedule ID on creation."""
    if (
        created
        and instance.activity
        and instance.activity.triggers_payment_email
    ):
        send_activity_created_email(instance.activity)


@receiver(
    post_save,
    sender=Activity,
    dispatch_uid="send_activity_payment_email_on_save",
)
def send_activity_payment_email_on_save(sender, instance, created, **kwargs):
    """Send payment email when Activity is saved."""
    if not instance.triggers_payment_email:
        return
    send_activity_updated_email(instance)


@receiver(
    post_delete,
    sender=Activity,
    dispatch_uid="send_activity_payment_email_on_delete",
)
def send_activity_payment_email_on_delete(sender, instance, **kwargs):
    """Send payment email when Activity is deleted."""
    if not instance.triggers_payment_email:
        return
    send_activity_deleted_email(instance)


@receiver(post_save, sender=Rate, dispatch_uid="on_save_rate")
def set_needs_recalculation_on_save_rate(sender, instance, created, **kwargs):
    """Set "needs update" flag when changing a rate."""
    if not created:
        Rate.objects.filter(pk=instance.pk).update(needs_recalculation=True)
        instance.refresh_from_db()


@receiver(post_save, sender=Price, dispatch_uid="on_save_price")
def save_payment_schedule_on_save_price(sender, instance, created, **kwargs):
    """Save payment schedule too when saving price."""
    if instance.payment_schedule:
        instance.payment_schedule.save()


@receiver(
    post_save,
    sender=PaymentSchedule,
    dispatch_uid="generate_payments_on_post_save",
)
def generate_payments_on_post_save(sender, instance, created, **kwargs):
    """Generate payments for activity before saving."""
    if instance.is_ready_to_generate_payments():
        activity = instance.activity

        vat_factor = activity.vat_factor

        if not instance.payments.exists():
            # Generate payments once, sync or regenerate afterwards.
            instance.generate_payments(
                activity.start_date, activity.end_date, vat_factor
            )
        else:
            # If status is either STATUS_DRAFT or STATUS_EXPECTED we delete
            # and regenerate payments.
            if activity.status in [STATUS_DRAFT, STATUS_EXPECTED]:
                instance.payments.all().delete()
                instance.generate_payments(
                    activity.start_date, activity.end_date, vat_factor
                )
            else:
                instance.synchronize_payments(
                    activity.start_date, activity.end_date, vat_factor
                )
                instance.recalculate_prices()
