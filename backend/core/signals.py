# Copyright (C) 2019 Magenta ApS, http://magenta.dk.
# Contact: info@magenta.dk.
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.


from django.db.models.signals import pre_save, post_save, post_delete
from django.dispatch import receiver
from core.models import Activity, STATUS_GRANTED, STATUS_EXPECTED, STATUS_DRAFT
from core.utils import (
    send_activity_created_email,
    send_activity_updated_email,
    send_activity_expired_email,
)


@receiver(post_save, sender=Activity)
def send_activity_payment_email_on_save(sender, instance, created, **kwargs):
    if not instance.triggers_payment_email:
        return
    if created:
        send_activity_created_email(instance)
    else:
        send_activity_updated_email(instance)


@receiver(post_delete, sender=Activity)
def send_activity_payment_email_on_delete(sender, instance, **kwargs):
    if not instance.triggers_payment_email:
        return
    send_activity_expired_email(instance)


@receiver(pre_save, sender=Activity)
def generate_payments_on_pre_save(sender, instance, **kwargs):
    try:
        current_object = sender.objects.get(pk=instance.pk)
        old_status = current_object.status
    except sender.DoesNotExist:
        old_status = instance.status

    if not instance.payment_plan:
        return

    vat_factor = instance.vat_factor
    if instance.payment_plan.payments.exists():
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
    else:
        instance.payment_plan.generate_payments(
            instance.start_date, instance.end_date, vat_factor
        )
