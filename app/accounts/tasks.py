from celery import shared_task
from django.core.management import call_command


@shared_task
def delete_inactivate_emails():
    """In this task we check if db is ready
    and then we run the command to delete the
    inactive emails who hour is greater than 1 hour"""
    call_command("wait_for_db")
    call_command("delete_inactive_mails")
