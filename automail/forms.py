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
        exclude = ('user', 'created_datetime')
        

class EmailForm(forms.ModelForm):

    class Meta:

        model = EmailCampaignTemplate
        exclude = (  'completed', 'created_datetime', 'sent_count', 
                    'failed_count', 'failed_emails', 'error', )
