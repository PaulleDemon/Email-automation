import pytz

from django import forms
from django.utils import timezone

from .models import (EmailTemplate, EmailTemplateAttachment, EmailConfiguration, 
                     EmailCampaign, EmailCampaignTemplate
                     )


class EmailConfigurationForm(forms.ModelForm):

    class Meta:
        model = EmailConfiguration
        exclude = ('user', 'use_ssl', 'is_verified')
        required = ('schedule',)


class EmailTemplateForm(forms.ModelForm):

    class Meta:
        
        model = EmailTemplate
        exclude = ('user', 'copy_count')


class AttachmentForm(forms.ModelForm):

    class Meta:

        model = EmailTemplateAttachment
        exclude = ('template', )


class EmailCampaignForm(forms.ModelForm):

    class Meta:
        model = EmailCampaign
        exclude = ('user', 'created_datetime', 'discontinued')
        
        

class EmailForm(forms.ModelForm):

    user_timezone = forms.ChoiceField(
        label="User Time Zone",
        choices=((tz, tz) for tz in pytz.common_timezones),
        widget=forms.Select(),
    )

    class Meta:

        model = EmailCampaignTemplate
        exclude = (  'completed', 'created_datetime', 'sent_count', 
                    'failed_count', 'failed_emails', 'error', 'smtp_error_count')

    def clean_schedule(self):
        local_datetime = self.cleaned_data.get('schedule')
        user_timezone = self.data.get('user_timezone')

        if local_datetime and user_timezone:
            user_tz = pytz.timezone(user_timezone)
            local_datetime = user_tz.localize(local_datetime)
            local_datetime = local_datetime.astimezone(pytz.utc)

        return local_datetime