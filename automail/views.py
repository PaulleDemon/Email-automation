from django.forms import model_to_dict
from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required

from .forms import EmailTemplateForm, AttachmentForm
from .models import EmailTemplate, EmailCampaign, EmailTemplateAttachment


@login_required
@require_http_methods(['GET', 'POST'])
def email_template_create(request):
    
    if request.method == 'GET':
        
        edit = request.GET.get('edit')

        context = {
            'subject': '',
            'body': '',
            'template_name': '',
            'variables': '',
            'attachements': []
        }

        if edit:

            try:
                int(edit)
            except ValueError:
                return render(request, '404.html') 


            template = EmailTemplate.objects.filter(id=edit)

            if not template.exists():
                return render(request, '404.html')

            if template.filter(user=request.user).exists():
                
                template_get = template.get(user=request.user)
                context = {
                    'id': template_get.id,
                    'subject': template_get.subject,
                    'body': template_get.body,
                    'variables': template_get.variables,
                    'attachments': template_get,
                }

            elif template.filter(public=True).exists():
                
                dup_temp = template.last()

                kwargs = model_to_dict(dup_temp, exclude=['user', 'name', 'public'])

                EmailTemplate.objects.create(user=request.user, name=f'{dup_temp.name} (copy)', public=False, **kwargs)


        return render(request, 'email-template-create.html', context=context)
    
    if request.method == 'POST':


        edit = request.GET.get('edit')

        template_form = EmailTemplateForm(request.POST)

        if edit:
            try:
                int(edit)

            except ValueError:
                return render(request, '404.html') 

            email_template = EmailTemplate.objects.filter(id=edit)

            if not email_template.exists() or (email_template.last().public == False and email_template.last().user != request.user):
                return render(request, '404.html') 


        if template_form.is_valid():

            file_form = AttachmentForm(request.POST, request.FILES)
            template = template_form.save(commit=False)

            print("Public: ", template.public, request.POST)
            # for updating id is required

            if request.FILES:
                # if there are attachment check if the form is valid before
                if file_form.is_valid():
                    if edit:
                        template = EmailTemplate.objects.filter(id=edit, user=request.user).update(**template_form.cleaned_data)
                    else:
                        template = template_form.save(commit=True)
                        template.user = request.user
                        template.save()

                    EmailTemplateAttachment.objects.filter(template=template).delete()

                    for f in request.FILES.getlist('file'):
                        EmailTemplateAttachment.objects.create(template=template, attachment=f)

                else:
                    return render(request, 'email-template-create.html', {'error': ['error with file']})
            
            else:
                
                if edit:
                    template = EmailTemplate.objects.filter(id=edit).update(**template_form.cleaned_data)
                    EmailTemplateAttachment.objects.filter(template=template).delete()

                else:
                    template = template_form.save(commit=False)
                    template.user = request.user
                    template.save()

            return redirect('email-templates')

        else:
            error = template_form.errors.as_data()
            errors = [f'{list(error[x][0])[0]}' for x in error]
            print("errors: ", template_form.errors)
            return render(request, 'email-template-create.html', {'error': errors})

    return render(request, 'email-template-create.html')


@login_required
@require_http_methods(['POST'])
def email_template_delete(request, id):

    try:
        EmailTemplate.objects.get(user=request.user, id=id).delete()

    except EmailTemplate.DoesNotExist:
        return render(request, '404.html')

    return redirect('email-templates')


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



