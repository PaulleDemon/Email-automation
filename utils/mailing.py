import time
import random
import smtplib
import imaplib
import mimetypes

import jinja2

from email.mime.text import MIMEText

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
    
  
def check_recipient_responded(email, start_date, end_date, imap_client: imaplib.IMAP4):
    """
        Given a mail id the function test if the 
        reipient has replied between a specified datetime
    """

    if settings.DEBUG:
        return random.choice([True, False])

    imap_client.select("INBOX")
    # Search for emails based on sender and date range
    search_criteria = f'(FROM "{email}") SINCE "{start_date}" BEFORE "{end_date}"'
    result, email_ids = imap_client.search(None, search_criteria)

    imap_client.close()

    if result == 'OK':
        email_ids = email_ids[0].split()
        if email_ids:
            return True
        
    return False