import bs4
import imaplib
import email_validator

from django.core.files.uploadedfile import UploadedFile

from automail.models import BlacklistedEmailDomains

"""
resused functionss
"""

def get_name_from_email(email):
    name, domain = email.split('@')
    return name.replace('.', ' ').strip().capitalize()


def get_file_size(request_file: UploadedFile, unit: str='MB'):
    """
    Get the file size from a file uploaded via request.FILES and convert it to KB or MB.

    """
    if unit not in ('KB', 'MB'):
        raise ValueError("Invalid unit. Please use 'KB' or 'MB'.")

    file_size_bytes = request_file.size

    if unit == 'MB':
        file_size = file_size_bytes / (1024 * 1024)  # 1 MB = 1024 KB
    else:
        file_size = file_size_bytes / 1024  # 1 KB = 1024 bytes

    return file_size


def get_plain_text_from_html(html_content: str):
    
    html_content = html_content.replace("<br>", "\n")
    soup = bs4.BeautifulSoup(html_content, "html.parser")

    # Extract the plain text
    plain_text = soup.get_text()
    return plain_text


def is_valid_mail(email: str):
    email_validator.SPECIAL_USE_DOMAIN_NAMES    

    try:
        validated_email = email_validator.validate_email(email)

    except email_validator.EmailNotValidError:
        return None
    
    if BlacklistedEmailDomains.objects.filter(domain__in=[validated_email.domain]).exists():
        return None
    
    return validated_email.normalized.lower()

