from django import forms

from .models import (EmailTemplate, EmailTemplateAttachment, EmailConfiguration)


class EmailConfigurationForm(forms.ModelForm):

    class Meta:
        model = EmailConfiguration
        exclude = ('user', 'use_ssl')


class EmailTemplateForm(forms.ModelForm):

    class Meta:
        
        model = EmailTemplate
        exclude = ('user',)


class AttachmentForm(forms.ModelForm):

    class Meta:

        model = EmailTemplateAttachment
        exclude = ('template', )