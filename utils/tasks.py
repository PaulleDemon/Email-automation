import io
import json
import time
import imaplib
import smtplib
import requests
import traceback
import pandas as pd

from email.mime.text import MIMEText

from celery import shared_task
from celery.utils.log import get_task_logger

from django.conf import settings
from django.db import transaction
from django.utils import timezone
from django.core.files.storage import default_storage
from django.core.mail import send_mass_mail, send_mail
from django.core.mail.backends.smtp import EmailBackend

from django_celery_beat.models import PeriodicTask

from automail.models import (EmailCampaignTemplate, EmailTemplateAttachment, 
                                EMAIL_SEND_RULES)

from .common import get_plain_text_from_html, is_valid_mail
from .mailing import send_mass_html_mail, send_email_with_attachments, check_recipient_responded

logger = get_task_logger(__name__)


@shared_task
def send_html_mail_celery(subject, message, html_message, from_email=None, recipient_list=[]):
    send_mass_html_mail(subject, message, html_message, from_email, recipient_list)


@shared_task
def send_mass_mail_celery(subject, message, from_email=None, recipient_list=[]):
    send_mass_mail([(subject, message, from_email, recipient_list)])


@shared_task
def send_mail_celery(subject, message, from_email=None, recipient_list=[]):
    logger.log(1, f"log: {recipient_list}")
    send_mail(subject, message, from_email=from_email, recipient_list=recipient_list)


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
			task = PeriodicTask.objects.get(name=taskid)

		except PeriodicTask.DoesNotExist:
			return

		task.enabled = False
		task.save()
                

@transaction.atomic
@shared_task(name='run_schedule_email')
def run_schedule_email(campaign_id):

    if settings.DEBUG:
        logger.info(f"working {campaign_id}")
    imap_client = None

    try:
        campaign = EmailCampaignTemplate.objects.get(id=campaign_id)
        subject = campaign.template.subject
        body = campaign.template.body
        sheet = campaign.campaign.file
        extension = sheet.name.split('.')[-1]

        if campaign.schedule == False:
             return

        if settings.DEBUG:
            url = settings.MEDIA_DOMAIN + sheet.url

        else:
            url = sheet.url

        response = requests.get(url, timeout=20)  # Fetch CSV data from the URL
        # logger.info(f"media url {settings.MEDIA_DOMAIN + sheet.url}")

        if response.status_code not in [200, 201]:
            logger.info(f"request exited with status {response.status_code}")
            campaign = EmailCampaignTemplate.objects.filter(id=campaign_id).update(error="request error {response.status_code}")

            return
            

        if extension.lower() == 'csv':
            data = pd.read_csv(io.StringIO(response.text))

        elif extension.lower() == 'xls':
            data = pd.read_excel(io.BytesIO(response.content))

        elif extension.lower() == 'xlsx':
            data = pd.read_excel(io.BytesIO(response.content), engine='openpyxl')
             
        else:
            logger.info(f"File doesn't have proper extension")
            raise Exception("File doesn't have a csv, xls, or xlsx extension")

        email_lookup = campaign.campaign.email_lookup

        data = data.drop_duplicates(subset=[email_lookup]) # drop duplicate emails
      
        data[email_lookup] = data[email_lookup].apply(is_valid_mail)
        # Remove rows with invalid email addresses (where 'Email' is None)
        data = data.dropna(subset=[email_lookup])

        # print("data: ", data)
       
        first_schedule = EmailCampaignTemplate.objects.filter(campaign=campaign.campaign).first().schedule.strftime("%d-%b-%Y")
        now_time = timezone.now().strftime("%d-%b-%Y")

        try:
            imap_client = imaplib.IMAP4_SSL(campaign.email.imap_host)
            imap_client.login(campaign.email.email, campaign.email.password)
        
        except imaplib.IMAP4.error:
            imap_client = None

        if campaign.email_send_rule == EMAIL_SEND_RULES.ALL:
            pass

        elif campaign.email_send_rule == EMAIL_SEND_RULES.NOT_RESPONDED:
            data['has_responded'] = data[email_lookup].apply(check_recipient_responded, args=(first_schedule, now_time, imap_client))
            data = data.dropna(subset=[email_lookup]) # remove invalid email
            # Remove rows where the recipient has not responded
            data = data[~data['has_responded']]
            data = data.drop(columns='has_responded')

        elif campaign.email_send_rule == EMAIL_SEND_RULES.RESPONDED:
            data['has_responded'] = data[email_lookup].apply(check_recipient_responded, args=(first_schedule, now_time, imap_client))
            data = data.dropna(subset=[email_lookup]) # remove invalid email
            # Remove rows where the recipient has responded
            data = data[data['has_responded']]
            data = data.drop(columns='has_responded')

        plain_body = get_plain_text_from_html(body)
       

        html_context = {
            'from_name': campaign.email.name,
            'from_email': campaign.email.email,
            'from_signature': campaign.email.signature,
        }

        smtp_settings = {
                'host': campaign.email.host,
                'port': campaign.email.port,
                'use_ssl': True if campaign.email.port == 465 else False,
                'use_tls': True if campaign.email.port == 587 else False,
                'username': campaign.email.email,
                'password': campaign.email.password,
        }

        attachments = []
        attachment_names = EmailTemplateAttachment.objects.filter(template=campaign.template).values_list('attachment', flat=True)
        
        for attachment_name in attachment_names:
            attachment = default_storage.open(attachment_name)
            attachments.append(attachment)


        for _, row_dict in data.iterrows():
            email_address = row_dict[campaign.campaign.email_lookup]
            recipient_list = [email_address]

            if campaign.smtp_error_count > 10:
                campaign.error += "\nToo many failed failed emails"
                campaign.campaign.discontinued = True
                campaign.save()         
                return

            try:
            
                connection = EmailBackend(fail_silently=False, **smtp_settings)

                html_context.update(row_dict)

                send_email_with_attachments(
                    subject=subject,
                    text_message=plain_body,
                    html_message=body,
                    html_context=html_context,
                    from_email=campaign.email.email,
                    recipient_list=recipient_list,
                    attachments=attachments,
                    connection=connection,
                    imap_client=imap_client
                )
                # logger.info(f"mail sent")

                campaign.sent_count += 1
                campaign.save()

            except (smtplib.SMTPAuthenticationError) as e:
                logger.info(f"Auth error {e}")
                campaign.campaign.discontinued = True
                campaign.error += '\nAuthentication error'
                campaign.save()
                return

            except (smtplib.SMTPSenderRefused, smtplib.SMTPRecipientsRefused) as e:
                logger.info(f"sender refused {e}")
                campaign.smtp_error_count += 1
                campaign.failed_emails += f"{email_address}, "
                campaign.save()         

            except Exception as e:
                campaign.failed_count += 1
                campaign.failed_emails += f"{email_address}, "
                campaign.save() 
                logger.info(f"exception: {e}")


            if campaign.sent_count % 10 == 0:
                time.sleep(0.5) # sleep half a second to allow other processes to continue

        campaign.completed = True
        campaign.scheduled = False
        campaign.save()

    except EmailCampaignTemplate.DoesNotExist as e:
        pass

    except (requests.RequestException) as e:
        campaign = EmailCampaignTemplate.objects.filter(id=campaign_id).update(error="request error occured")
        logger.info(f"request error: {e}")

    # except Exception as e:
    #     campaign = EmailCampaignTemplate.objects.filter(id=id).update(error=f"An error occurred on our end {e}")
    #     logger.info(f"Campaign error: {e}")
    #     traceback.format_exc()

    finally:

        disable_periodic_task(f'email_{campaign_id}')

        if imap_client:
            imap_client.logout() 