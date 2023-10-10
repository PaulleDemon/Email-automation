import jinja2

from django.urls import reverse
from django.forms import model_to_dict
from django.shortcuts import render, redirect
from django.core.serializers.json import DjangoJSONEncoder
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required

from .forms import (EmailTemplateForm, AttachmentForm, EmailConfigurationForm, 
                        EmailCampaignForm, EmailFollowUpForm)
from .models import (EmailTemplate, EmailCampaign, EmailTemplateAttachment, 
                        EmailConfiguration, EMAIL_SEND_RULES)

from utils.mailing import test_email_credentials
from utils.tasks import send_html_mail_celery
from utils.decorators import login_required_for_post


jinja_env = jinja2.Environment()


@login_required_for_post
@require_http_methods(['GET', 'POST'])
def email_template_create(request):
    
    if request.method == 'GET':
        
        edit = request.GET.get('edit')
        copy = request.GET.get('copy')

        context = {
            'subject': '',
            'body': '',
            'template_name': '',
            'variables': '',
            'attachements': []
        }

        if edit:

            if not request.user.is_authenticated:
                return redirect('login')

            try:
                int(edit)
                template = EmailTemplate.objects.get(id=edit)
            except (ValueError, EmailTemplate.DoesNotExist):
                return render(request, '404.html') 

            if template.user == request.user:
                
                context = {
                    'template': template
                }

            elif template.public == True:
                
                dup_temp = template.last()

                kwargs = model_to_dict(dup_temp, exclude=['id', 'user', 'name', 'public'])

                temp = EmailTemplate.objects.create(id=None, user=request.user, name=f'{dup_temp.name} (copy)', public=False, **kwargs)
                modified_url = reverse('email-template-create') + f'?edit={temp.id}'

                return redirect(modified_url)

            else:
                return render(request, '404.html')


        if copy:

            if not request.user.is_authenticated:
                return redirect('login')

            try:
                int(copy)
            except ValueError:
                return render(request, '404.html') 


            template = EmailTemplate.objects.filter(id=copy)

            if not template.exists():
                return render(request, '404.html')

            dup_temp = template.last()
            dup_temp.copy_count += 1
            dup_temp.save()

            kwargs = model_to_dict(dup_temp, exclude=['id', 'user', 'name', 'public', 'copy_count'])

            temp = EmailTemplate.objects.create(id=None, user=request.user, name=f'{dup_temp.name} (copy)', public=False, **kwargs)
            # TODO: copy the attachments
            modified_url = reverse('email-template-create') + f'?edit={temp.id}'

            return redirect(modified_url)

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
            return render(request, 'email-template-create.html', {'error': errors, **request.POST})

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

    private_templates = EmailTemplate.objects.filter(user__id=request.user.id)

    public_templates = EmailTemplate.objects.filter(public=True)


    return render(request, 'email-templates.html', context={'private_templates': private_templates,
                                                            'public_templates': public_templates
                                                            })


@login_required_for_post
def campaign_create_view(request):

    templates = EmailTemplate.objects.filter(user__id=request.user.id)
    emails = EmailConfiguration.objects.filter(user__id=request.user.id)
    rules  = EMAIL_SEND_RULES.choices

    context = {
            'templates': list(templates.values('name', 'id')),
            'emails': list(emails.values('id', 'email')),
            'rules': rules,
            **request.POST
        }
    print("Post: ", request.POST.get('template'))

    if request.method == 'GET':
        pass

    else:
        edit = request.POST.get('edit')


        if not edit:
            pass


    return render(request, 'email-campaign-create.html', context)


def campaigns_view(request):

    return render(request, 'email-campaigns.html')


@login_required_for_post
@require_http_methods(['GET', 'POST'])
def configuration_create_view(request):

    """
        used to configure the server
    """
    if request.method == 'GET':
        edit = request.GET.get('edit')

        context = {}

        if edit:
            try:
                int(edit)
                configuration = EmailConfiguration.objects.get(id=edit)
                context['configuration'] = configuration

            except (ValueError, EmailConfiguration.DoesNotExist):
                return render(request, '404.html')
            
        return render(request, 'configure-server.html', context)

    else:
        edit = request.GET.get('edit')

        form = EmailConfigurationForm(request.POST)
        
        if form.is_valid():

            credentials = form.cleaned_data
            credentials_valid, error = test_email_credentials(email=credentials['email'], password=credentials['password'],
                                    host=credentials['host'], port=credentials['port'])
            
            if credentials_valid != True:
                return render(request, 'configure-server.html', context={'errors': [error], 'configuration': credentials})

            if edit:
                try:
                    int(edit)
                    configuration = EmailConfiguration.objects.get(id=edit)
            
                except (ValueError, EmailConfiguration.DoesNotExist):
                    return render(request, '404.html')

                EmailConfiguration.objects.filter(id=edit).update(**form.cleaned_data)      

            else:

                if EmailConfiguration.objects.filter(user=request.user, email=form.cleaned_data['email']).exists():
                    return render(request, 'configure-server.html', context={'errors': 'This email already exists'})

                configuration = form.save(commit=False)
                configuration.user = request.user
                configuration.save()

            return redirect('configurations')
        
        else:
            error = form.errors.as_data()
            errors = [f'{list(error[x][0])[0]}' for x in error] 

            return render(request, 'configure-server.html', context={'errors': errors})


def configurations_view(request):

    cofigurations = EmailConfiguration.objects.filter(user__id=request.user.id)

    return render(request, 'configurations.html', context={'configurations': cofigurations})


@login_required
def delete_configuration_view(request, id):

    try:
        EmailConfiguration.objects.get(id=id, user=request.user).delete()
        return redirect('configurations')   
    
    except (EmailConfiguration.DoesNotExist):
        return render(request, '404.html')


@login_required
@require_http_methods(['POST'])
def send_test_mail(request):

    variables = request.POST.get('variables')
    subject = request.POST.get('subject')
    body = request.POST.get('body')
    files = request.FILES

    jinja_env.from_string()