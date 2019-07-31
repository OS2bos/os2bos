from decimal import Decimal

from django.db.models.signals import pre_save, post_save, post_delete
from django.dispatch import receiver
from core.models import Activity
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

    vat_factor = Decimal("100")
    if instance.service_provider:
        vat_factor = instance.service_provider.vat_factor

    if not instance.payment_plan:
        return

    if instance.payment_plan.payments.exists():
        # If status is either STATUS_DRAFT or STATUS_EXPECTED or
        # the activity was just granted we delete and
        # regenerate payments.
        if instance.status in [
            Activity.STATUS_DRAFT,
            Activity.STATUS_EXPECTED,
        ] or (
            not old_status == Activity.STATUS_GRANTED
            and instance.status == Activity.STATUS_GRANTED
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
