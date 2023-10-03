from django import forms

from .models import EmailTemplate, EmailTemplateAttachment


class EmailTemplateForm(forms.ModelForm):

    class Meta:
        
        model = EmailTemplate
        exclude = ('user',)


class AttachmentForm(forms.ModelForm):

    class Meta:

        model = EmailTemplateAttachment
        exclude = ('template', )