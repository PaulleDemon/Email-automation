import re
import time
import random
import base64

from django.conf import settings

from celery import shared_task
from django.core.mail import send_mass_mail
from celery.utils.log import get_task_logger


from user.models import User

from .mailing import send_mass_html_mail, send_email_with_attachments

logger = get_task_logger(__name__)


@shared_task
def send_html_mail_celery(subject, message, html_message, from_email, recipient_list):
    send_mass_html_mail(subject, message, html_message, from_email, recipient_list)


@shared_task
def send_mass_mail_celery(subject, message, from_email=None, recipient_list=[]):
    send_mass_mail(subject, message, from_email, recipient_list)


@shared_task
def send_attachment_mail_celery(subject, message, html_message, context={}, from_email=None, recipient_list=[], attachments=[]):

    try:
        send_email_with_attachments(subject, message, html_message, context, from_email, recipient_list, attachments)
    except Exception:
        pass