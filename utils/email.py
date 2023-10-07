import smtplib
from django.conf import settings

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
