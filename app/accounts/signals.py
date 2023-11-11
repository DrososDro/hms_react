"""
Signals for account model
"""


from datetime import timedelta
from django.contrib.auth import get_user_model

from django.db.models.base import post_save
from accounts.tasks import delete_inactivate_emails


def call_command_delete_inactive_mail(sender, instance, created, **kwargs):
    """Call the command delete inactive mails after one hour"""
    if created:
        delete_inactivate_emails.apply_async(
            eta=instance.created_at + timedelta(minutes=61),
        )


post_save.connect(call_command_delete_inactive_mail, sender=get_user_model())
