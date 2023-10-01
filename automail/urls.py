from django.urls import path
from django.shortcuts import redirect

from .views import email_automation


urlpatterns = [
    
    path('', lambda request: redirect('email-template-create', permanent=True)),
    path('templates/', email_automation, name='email-template'),
    path('template/create/', email_automation, name='email-template-create'),
    
    path('campaigns/', email_automation, name='email-campaigns'),
    path('campaign/create/', email_automation, name='email-campaign-create'),

    # path('bulk/', )
]
