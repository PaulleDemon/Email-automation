import os
from django import template

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