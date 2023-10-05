from django.urls import path
from django.shortcuts import redirect

from .views import (email_template_create, email_templates, email_template_delete, configuration_view)

urlpatterns = [
    
    path('', lambda request: redirect('email-template-create', permanent=True)),
    path('templates/', email_templates, name='email-templates'),
    path('template/create/', email_template_create, name='email-template-create'),
    path('template/<int:id>/delete/', email_template_delete, name='email-template-delete'),
    
    path('campaigns/', email_template_create, name='email-campaigns'),
    path('campaign/create/', email_template_create, name='email-campaign-create'),

    path('configure/', configuration_view, name='configure-email')
]
