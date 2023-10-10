from django import forms

from .models import (EmailTemplate, EmailTemplateAttachment, EmailConfiguration, 
                     EmailCampaign, EmailCampaignTemplate
                     )


class EmailConfigurationForm(forms.ModelForm):

    class Meta:
        model = EmailConfiguration
        exclude = ('user', 'use_ssl')


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
        exclude = ('user', 'completed', 'created_datetime', 'send_count', 
                   'failed_count', 'failed_emails', 'error', 'email_send_rule')
        

class EmailFollowUpForm(forms.ModelForm):

    class Meta:

        model = EmailCampaign
        fields = ('email_send_rule', 'scheduled', 'schedule')
