from django.conf import settings
from django.dispatch import receiver
from django.db.models.signals import pre_save

from .models import Images
