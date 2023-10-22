import os
import pytz
from datetime import datetime

from django import template
from django.utils import timezone
from django.core import exceptions

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


@register.simple_tag
def utc_to_local(utc_datetime, user_timezone, date_format="%b. %d, %Y, %I:%M %p"):
   
    if not isinstance(utc_datetime, str):
        utc_datetime = str(utc_datetime)

    try:
        user_timezone = pytz.timezone(user_timezone)  

    except pytz.UnknownTimeZoneError:
        pass

    utc_datetime_obj = datetime.fromisoformat(utc_datetime)
    utc_datetime_obj = utc_datetime_obj.replace(tzinfo=pytz.UTC)
    
    specific_datetime = utc_datetime_obj.astimezone(user_timezone)
    print("date: ", specific_datetime, specific_datetime.strftime(date_format), date_format)
    return specific_datetime.strftime(date_format)
    