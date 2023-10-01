from django.db import models
from encrypted_model_fields.fields import EncryptedCharField, EncryptedEmailField

from user.models import User


class EmailConfiguration(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    host = models.CharField(max_length=350)
    use_ssl = models.BooleanField(default=True)
    port = models.SmallIntegerField(default=465) # use ssl port

    email = EncryptedEmailField()
    password = EncryptedCharField(max_length=100)



class EmailTemplate(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    subject = models.CharField(max_length=250, null=True, blank=True)

    template = models.TextField(max_length=10000)
    attachment = models.FileField(upload_to='attachments/', null=True, blank=True)
    datetime = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.template[:30]


class EmailCampaign(models.Model):

    name = models.CharField(max_length=30, default='campaign', null=True, blank=True)

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    file = models.FileField(upload_to='email-files/')
    completed = models.BooleanField(default=False)

    created_datetime = models.DateTimeField(auto_now=True)
    sent_count = models.PositiveIntegerField(default=0)

    failed_count = models.PositiveIntegerField(default=0)
    failed_emails = models.TextField(max_length=4000) 
    error = models.TextField(max_length=4000)

    follow_up = models.ForeignKey('self', null=True, blank=True ,on_delete=models.CASCADE)

    schedule = models.DateTimeField(null=True, blank=True)
    scheduled = models.BooleanField(default=False)


    def __str__(self) -> str:
        return f'{self.user}'
    

class EmailCampaignTemplate(models.Model):

    email = models.ForeignKey(EmailConfiguration, on_delete=models.CASCADE)
    campaign = models.ForeignKey(EmailCampaign, on_delete=models.CASCADE)
    template = models.ForeignKey(EmailTemplate, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return f'{self.campaign.name}'