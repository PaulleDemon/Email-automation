from django.urls import path
from django.shortcuts import redirect

from .views import email_template_create, email_templates

urlpatterns = [
    
    path('', lambda request: redirect('email-template-create', permanent=True)),
    path('templates/', email_templates, name='email-templates'),
    path('template/create/', email_template_create, name='email-template-create'),
    
    path('campaigns/', email_template_create, name='email-campaigns'),
    path('campaign/create/', email_template_create, name='email-campaign-create'),

    # path('bulk/', )
]
