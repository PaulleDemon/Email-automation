from datetime import datetime
from django.db import models

class TERMS_TYPE(models.IntegerChoices):

    PRIVACY = (0, 'privacy')
    T_AND_C = (1, 't&c')

class Terms(models.Model):

    title = models.CharField(max_length=50)
    description = models.TextField()
    info_type = models.PositiveSmallIntegerField(choices=TERMS_TYPE.choices, default=TERMS_TYPE.PRIVACY)
    datetime = models.DateTimeField(auto_now=True)

    class Meta:

        verbose_name = 't&c'
        verbose_name_plural = 't&c'

    def __str__(self):
        return f'{self.id}'
        