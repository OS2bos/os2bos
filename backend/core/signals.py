from django.db.models.signals import post_save, post_delete
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
