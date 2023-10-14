import io
import json
import time
import imaplib
import smtplib
import requests
import pandas as pd

from email.mime.text import MIMEText

from celery import shared_task
from celery.utils.log import get_task_logger

from django.conf import settings
from django.db import transaction
from django.core.mail import send_mass_mail, send_mail
from django.core.mail.backends.smtp import EmailBackend

from django_celery_beat.models import PeriodicTask

from automail.models import EmailCampaignTemplate, EmailTemplateAttachment

from .common import get_plain_text_from_html
from .mailing import send_mass_html_mail, send_email_with_attachments

logger = get_task_logger(__name__)


@shared_task
def send_html_mail_celery(subject, message, html_message, from_email, recipient_list):
    send_mass_html_mail(subject, message, html_message, from_email, recipient_list)


@shared_task
def send_mass_mail_celery(subject, message, from_email=None, recipient_list=[]):
    send_mass_mail([(subject, message, from_email, recipient_list)])


@shared_task
def send_mail_celery(subject, message, from_email=None, recipient_list=[]):
    send_mail(subject, message, from_email=None, recipient_list=[])


@shared_task
def send_attachment_mail_celery(subject, message, html_message, context={}, from_email=None, recipient_list=[], attachments=[]):

    try:
        send_email_with_attachments(subject, message, html_message, context, from_email, recipient_list, attachments)
    except Exception:
        pass


@shared_task(name='disable_periodic_task')
def disable_periodic_task(taskid):

	with transaction.atomic():
		try:
			task = PeriodicTask.objects.get(id=taskid)

		except PeriodicTask.DoesNotExist:
			return

		task.enabled = False
		task.save()
                
    
@shared_task
def run_schedule_email(id):
    try:
        campaign = EmailCampaignTemplate.objects.get(id=id)
        subject = campaign.template.subject
        body = campaign.template.body
        sheet = campaign.file
        extension = sheet.name.split('.')[-1]

        if extension.lower() == 'csv':
            response = requests.get(sheet.url)  # Fetch CSV data from the URL
            data = pd.read_csv(io.StringIO(response.text))

        elif extension.lower() in ['xls', 'xlsx']:
            response = requests.get(sheet.url)  # Fetch Excel data from the URL
            data = pd.read_excel(io.BytesIO(response.content))

        else:
            raise Exception("File doesn't have a csv, xls, or xlsx extension")

        plain_body = get_plain_text_from_html(body)

        imap_client = None

        try:
            imap_client = imaplib.IMAP4_SSL(campaign.email.imap_host)
            imap_client.login(campaign.email.email, campaign.email.password)
        
        except imaplib.IMAP4.error:
            imap_client = None

        for _, row_dict in data.iterrows():
            email_address = row_dict[campaign.campaign.email_lookup]
            recipient_list = [email_address]

            if campaign.smtp_error_count > 10:
                campaign.error += "\nToo many failed failed emails"
                campaign.campaign.discontinued = True
                campaign.save()         
                return

            try:
                # Create a new 'html_context' for each email
                html_context = {
                    'from_name': campaign.email.name,
                    'from_email': campaign.email.email,
                    'from_signature': campaign.email.signature,
                }

                smtp_settings = {
                     'host': campaign.email.host,
                     'port': campaign.email.port,
                     'use_ssl': campaign.email.use_ssl,
                     'username': campaign.email.email,
                     'password': campaign.email.password,
                }

                connection = EmailBackend(fail_silently=False, **smtp_settings)

                html_context.update(row_dict)

                send_email_with_attachments(
                    subject=subject,
                    text_message=plain_body,
                    html_message=body,
                    html_context=html_context,
                    from_email=campaign.email.email,
                    recipient_list=recipient_list,
                    attachments=list(EmailTemplateAttachment.objects.filter(template=campaign.template)),
                    connection=connection,
                    imap_client=imap_client
                )

                campaign.sent_count += 1
                campaign.save()

            except (smtplib.SMTPAuthenticationError):
                campaign.campaign.discontinued = True
                campaign.save()
                return

            except (smtplib.SMTPSenderRefused, smtplib.SMTPRecipientsRefused):
                campaign.smtp_error_count += 1
                campaign.failed_emails += f"{email_address}, "
                campaign.save()         

            except Exception as e:
                campaign.failed_count += 1
                campaign.failed_emails += f"{email_address}, "
                campaign.save()         

            if campaign.sent_count % 10 == 0:
                 time.sleep(0.5) # sleep half a second to allow other processes to continue

    except EmailCampaignTemplate.DoesNotExist as e:
        pass

    except (requests.RequestException) as e:
        campaign = EmailCampaignTemplate.objects.filter(id=id).update(error="request error occured")

    except Exception:
        pass

    finally:
        if imap_client:
            imap_client.logout() 
            imap_client.close()