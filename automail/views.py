from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods

from .forms import EmailTemplateForm, AttachmentForm
from .models import EmailTemplate, EmailCampaign, EmailTemplateAttachment


@require_http_methods(['GET', 'POST'])
def email_template_create(request):
   
    if request.method == 'GET':
        return render(request, 'email-template-create.html')
    
    if request.method == 'POST':

        template_form = EmailTemplateForm(request.POST)

        if template_form.is_valid():

            file_form = AttachmentForm(request.POST, request.FILES)
            template = template_form.save(commit=False)

            if request.FILES:

                if file_form.is_valid():
                    template.user = request.user
                    template.save()

                    for f in request.FILES.getlist('file'):
                        EmailTemplateAttachment.objects.create(template=template, attachment=f)

                else:
                    return render(request, 'email-template-create.html', {'error': ['error with file']})
            
            template.user = request.user
            template.save()

            return redirect('email-templates')

        else:
            return render(request, 'email-template-create.html')

    return render(request, 'email-template-create.html')


@require_http_methods(['GET'])
def email_templates(request):

    private_templates = EmailTemplate.objects.filter(user=request.user)

    public_templates = EmailTemplate.objects.filter(public=True)


    return render(request, 'email-templates.html', context={'private_templates': private_templates,
                                                            'public_templates': public_templates
                                                            })

@require_http_methods(['GET'])
def campaign_view(request):

    return render(request, 'email-campaign.html')



