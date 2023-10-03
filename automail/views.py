from django.shortcuts import render
from django.views.decorators.http import require_http_methods

from .models import EmailTemplate, EmailCampaign


@require_http_methods(['GET', 'POST'])
def email_template_create(request):
   
    if request.method == 'GET':
        return render(request, 'email-template-create.html')
    
    return render(request, 'email-template-create.html')


@require_http_methods(['GET'])
def email_templates(request):

    private_templates = EmailTemplate.objects.filter(user=request.user)

    public_templates = EmailTemplate.objects.filter(public=True)


    return render(request, 'email-templates.html', context={'private_templates': private_templates,
                                                            'public_templates': public_templates
                                                            })




