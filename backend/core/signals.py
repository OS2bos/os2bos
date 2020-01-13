# Copyright (C) 2019 Magenta ApS, http://magenta.dk.
# Contact: info@magenta.dk.
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
"""Signals for acting on events occuring on model objects."""

from django.db.models.signals import pre_save, post_save, post_delete
from django.dispatch import receiver
from core.models import (
    Activity,
    PaymentSchedule,
    Payment,
    STATUS_GRANTED,
    STATUS_EXPECTED,
    STATUS_DRAFT,
)
from core.utils import (
    send_activity_created_email,
    send_activity_updated_email,
    send_activity_expired_email,
)


@receiver(post_save, sender=Payment)
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


@receiver(post_save, sender=PaymentSchedule)
def set_payment_id_on_paymentschedule_save(
    sender, instance, created, **kwargs
):
    """Set the payment_id as the PaymentSchedule ID on creation."""
    if created:
        instance.payment_id = instance.id
        instance.save()


@receiver(post_save, sender=Activity)
def send_activity_payment_email_on_save(sender, instance, created, **kwargs):
    """Send payment email when Activity is saved."""
    if not instance.triggers_payment_email:
        return
    if created:
        send_activity_created_email(instance)
    else:
        send_activity_updated_email(instance)


@receiver(post_delete, sender=Activity)
def send_activity_payment_email_on_delete(sender, instance, **kwargs):
    """Send payment email when Activity is deleted."""
    if not instance.triggers_payment_email:
        return
    send_activity_expired_email(instance)


@receiver(pre_save, sender=Activity)
def generate_payments_on_pre_save(sender, instance, **kwargs):
    """Generate payments for activity before saving."""
    try:
        current_object = sender.objects.get(pk=instance.pk)
        old_status = current_object.status
        created = False
    except sender.DoesNotExist:
        old_status = instance.status
        created = True

    if not instance.payment_plan:
        return

    vat_factor = instance.vat_factor

    if created:
        instance.payment_plan.generate_payments(
            instance.start_date, instance.end_date, vat_factor
        )
    elif instance.payment_plan.payments.exists():
        # If status is either STATUS_DRAFT or STATUS_EXPECTED or
        # the activity was just granted we delete and
        # regenerate payments.
        if instance.status in [STATUS_DRAFT, STATUS_EXPECTED] or (
            not old_status == STATUS_GRANTED
            and instance.status == STATUS_GRANTED
        ):
            instance.payment_plan.payments.all().delete()
            instance.payment_plan.generate_payments(
                instance.start_date, instance.end_date, vat_factor
            )
        else:
            instance.payment_plan.synchronize_payments(
                instance.start_date, instance.end_date, vat_factor
            )
