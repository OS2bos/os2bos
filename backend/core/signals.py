from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from core.models import Activity, Appropriation
from core.utils import send_activity_created_email, send_activity_changed_email


@receiver(post_save, sender=Activity)
def send_activity_payment_email(sender, instance, created, **kwargs):
    send_mail("test", "test", "test@test.dk", ["test@test.dk"])
    # If activity or appropriation is not granted we don't send an email.
    if (
        not instance.status == Activity.STATUS_GRANTED
        or not instance.appropriation.status == Appropriation.STATUS_GRANTED
    ):
        return

    # Don't trigger the email if the payment plan does not exist
    # or does not need a payment email to trigger.
    if not hasattr(instance, "payment_plan"):
        return
    if not instance.payment_plan.triggers_payment_email():
        return

    if created:
        send_activity_created_email(instance)
    else:
        send_activity_changed_email(instance)
