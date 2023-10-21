import os
from django import template
from django.utils import timezone

register = template.Library()


@register.filter
def filename(value):
    """
        returns just the file name
    """
    return os.path.basename(value.name)

@register.filter
def subtract(value, arg):
    return value - arg

@register.filter
def utc_to_local(utc_datetime):
    if utc_datetime:
        return timezone.localtime(utc_datetime)
    return None
