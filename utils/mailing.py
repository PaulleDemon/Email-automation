import smtplib
import jinja2
from django.core.mail import get_connection, EmailMultiAlternatives

from django.conf import settings
from django.core.mail import EmailMultiAlternatives

jinja_env = jinja2.Environment()


def send_mass_html_mail(subject: str, message: str, html_message, from_email, recipient_list: list):
    emails = []
    for recipient in recipient_list:
        email = EmailMultiAlternatives(subject, message, from_email, [recipient])
        email.attach_alternative(html_message, 'text/html')
        emails.append(email)

    return get_connection().send_messages(emails)


def test_email_credentials(email, password, host, port):

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

    return (True, "valid credentials")


def send_email_with_attachments(subject, text_message, html_message, html_context={}, from_email=None, recipient_list=[], attachments=None):
    
    subject_template = jinja_env.from_string(subject)
    subject = subject_template.render(html_context)
    
    html_template = jinja_env.from_string(html_message)
    html_message = html_template.render(html_context)

    plain_template = jinja_env.from_string(text_message)
    text_message = plain_template.render(html_context)

    email = EmailMultiAlternatives(subject, text_message, from_email, recipient_list)
    email.attach_alternative(html_message, "text/html") 

    if attachments:
        # Attach multiple files to the email
        for attachment in attachments:
            email.attach(attachment.name, attachment.read(), attachment.content_type)

    try:
        # Send the email
        # email.send()
        return get_connection().send_messages([email])
    
    except Exception as e:
        # Handle any exceptions here (e.g., log the error)
        print(f"Error sending email: {e}")
        return False