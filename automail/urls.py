from django.urls import path
from django.shortcuts import redirect

from .views import (email_template_create, email_templates, email_template_delete, 
                        campaign_create_view, campaigns_view, delete_campaign_view,
                        configuration_create_view, configurations_view, delete_configuration_view, 
                        send_test_mail_view, detailed_template_view
                        )

urlpatterns = [
    
    path('', lambda request: redirect('email-templates', permanent=True)),
    path('templates/', email_templates, name='email-templates'),
    path('template/create/', email_template_create, name='email-template-create'),
    path('template/<int:id>/delete/', email_template_delete, name='email-template-delete'),
    
    path('campaigns/', campaigns_view, name='email-campaigns'),
    path('campaign/create/', campaign_create_view, name='email-campaign-create'),
    path('campaign/<int:id>/delete/', delete_campaign_view, name='email-campaign-delete'),

    path('configure/add/', configuration_create_view, name='configure-email'),
    path('configure/<int:id>/delete/', delete_configuration_view, name='configure-email-delete'),
    path('configurations/', configurations_view, name='configurations'),
    
    path('send-test-mail/', send_test_mail_view, name='test-mail-view'),

    path('<int:id>/view-mail/', detailed_template_view, name='detailed-template-view')
]
