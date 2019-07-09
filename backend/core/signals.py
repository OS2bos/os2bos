from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from core.models import Activity, Appropriation
from core.utils import (
    send_activity_created_email,
    send_activity_updated_email,
    send_activity_deleted_email,
)


@receiver(post_save, sender=Activity)
def send_activity_payment_email_on_save(sender, instance, created, **kwargs):
    # If activity or appropriation is not granted we don't send an email.
    if (
        not instance.status == Activity.STATUS_GRANTED
        or not instance.appropriation.status == Appropriation.STATUS_GRANTED
    ):
        return

    # Don't trigger the email if the payment plan does not exist
    # or does not need a payment email to trigger.
    if not hasattr(instance, "payment_plan") or not instance.payment_plan:
        return
    if not instance.payment_plan.triggers_payment_email():
        return

    if created:
        send_activity_created_email(instance)
    else:
        send_activity_updated_email(instance)


@receiver(post_delete, sender=Activity)
def send_activity_payment_email_on_delete(sender, instance, **kwargs):
    # If activity or appropriation is not granted we don't send an email.
    if (
        not instance.status == Activity.STATUS_GRANTED
        or not instance.appropriation.status == Appropriation.STATUS_GRANTED
    ):
        return

    # Don't trigger the email if the payment plan does not exist
    # or does not need a payment email to trigger.
    if not hasattr(instance, "payment_plan") or not instance.payment_plan:
        return
    if not instance.payment_plan.triggers_payment_email():
        return
    send_activity_deleted_email(instance)
