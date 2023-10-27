import time
import pytz
import random
import smtplib
import imaplib
import mimetypes

import jinja2

from datetime import datetime

from email.mime.text import MIMEText
from email import utils, message_from_string


from django.conf import settings
from django.core.mail.backends.smtp import EmailBackend
from django.core.mail import get_connection, EmailMultiAlternatives

jinja_env = jinja2.Environment()


def send_mass_html_mail(subject: str, message: str, html_message, from_email, recipient_list: list):
    emails = []
    for recipient in recipient_list:
        email = EmailMultiAlternatives(subject, message, from_email, [recipient])
        email.attach_alternative(html_message, 'text/html')
        emails.append(email)

    return get_connection().send_messages(emails)


def test_email_credentials(email, password, host, port, imap_host):

    if settings.DEBUG:
        return (True, "valid")

    server = smtplib.SMTP(host, port, timeout=30.0)
    server.starttls()

    try:
        # Log in to the email account
        server.login(email, password)   

    except smtplib.SMTPAuthenticationError:
        return (False, "Invalid credentials.")
    
    except Exception as e:
        return (False, f"An error occurred: {e}")

    finally:
        # Close the server connection
        server.quit()

    if imap_host:
        try:
            with imaplib.IMAP4_SSL(imap_host) as client:
                client.login(email, password)
        
        except imaplib.IMAP4.error:
            return (False, "Invalid Imap credentials")

    return (True, "valid credentials")


def send_email_with_attachments(subject, text_message, html_message, html_context={}, 
                                from_email=None, recipient_list=[], attachments=None, \
                                connection=None, imap_client:imaplib.IMAP4=None):
    # TODO: in the future enable user to save the sent mail to inbox
    subject_template = jinja_env.from_string(subject)
    subject = subject_template.render(html_context)
    
    html_template = jinja_env.from_string(html_message)
    html_message = html_template.render(html_context)

    plain_template = jinja_env.from_string(text_message)
    text_message = plain_template.render(html_context)

    email = EmailMultiAlternatives(subject, text_message, from_email, recipient_list, connection=connection or get_connection())
    email.attach_alternative(html_message, "text/html") 

    # if imap_client:
    #     imap_client.append('INBOX.Sent', '\\Seen', imaplib.Time2Internaldate(time.time()), plain_template.encode('utf8'))

    if attachments:
        # Attach multiple files to the email
        for attachment in attachments:
            content_type, _ = mimetypes.guess_type(attachment.name)
            if content_type is None:
                content_type = 'application/octet-stream'  # Fallback content type

            email.attach(attachment.name, attachment.read(), content_type)
    
    
    return email.send()
    


def check_recipient_responded(email_address, start_date: datetime, end_date, imap_client: imaplib.IMAP4):
    """
        Given a mail id the function test if the 
        reipient has replied between a specified datetime4

        NOTE: start_date and end_date must be in UTC
    """

    if settings.DEBUG:
        return random.choice([True, False])

    imap_client.select("INBOX")
    # Search for emails based on sender and date range

    start_date = start_date.replace(tzinfo=pytz.UTC)
    end_date = end_date.replace(tzinfo=pytz.UTC)

    start_date_str = start_date.strftime("%d-%b-%Y")
    end_date_str = end_date.strftime("%d-%b-%Y")
        
    # search_criteria = f'(FROM "{email}") SINCE "{start_date_str}" BEFORE "{end_date_str}"'
    search_criteria = f'(FROM "{email_address}") SENTSINCE "{start_date_str}" SENTSINCE "{end_date_str}"'
    result, email_ids = imap_client.search(None, search_criteria)
  
    if result == 'OK':
        email_ids = email_ids[0].split()

        if email_ids:
            for email_id in email_ids:
                # Fetch the email and process its sent date and time
                email_data = imap_client.fetch(email_id, "(BODY[HEADER.FIELDS (DATE)])")
                
                # Extract the sent date from email_data
                msg = message_from_string(email_data[1][0][1].decode("utf-8"))
            
                # sent_date_str = email_data[1][0][1].decode("utf-8").strip()
                # sent_date = datetime.strptime(sent_date_str, 'Date: %a, %d %b %Y %H:%M:%S %z')
                sent_date = datetime.fromtimestamp(utils.mktime_tz(utils.parsedate_tz(msg["Date"])))
            
                # Convert sent_date to the common timezone (UTC)
                sent_date = sent_date.astimezone(pytz.utc)
                # Compare the sent date with the desired start_datetime and end_datetime
                if start_date <= sent_date <= end_date:
                    return True
        
    return False