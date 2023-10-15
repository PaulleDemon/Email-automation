import json
import jinja2


from django.db import models
from django.urls import reverse
from django.conf import settings
from django.utils import timezone
from django.http import JsonResponse
from django.forms import model_to_dict
from django.core.paginator import Paginator
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.core.serializers.json import DjangoJSONEncoder, Serializer
from django.db.models import Q, F, BooleanField, Case, When, Value, Count, OuterRef, Subquery

from django_ratelimit.decorators import ratelimit

from .forms import (EmailTemplateForm, AttachmentForm, EmailConfigurationForm, 
                        EmailCampaignForm, EmailForm)
from .models import (EmailTemplate, EmailCampaign, EmailTemplateAttachment, 
                        EmailConfiguration, EmailCampaignTemplate, EMAIL_SEND_RULES)

from utils.tasks import send_attachment_mail_celery
from utils.common import get_file_size, get_plain_text_from_html
from utils.mailing import test_email_credentials, send_email_with_attachments
from utils.decorators import login_required_for_post, login_required_rest_api


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
                
                kwargs = model_to_dict(template, exclude=['id', 'user', 'name', 'public'])

                temp = EmailTemplate.objects.create(id=None, user=request.user, name=f'{template.name} (copy)', public=False, **kwargs)
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

    public = request.GET.get('public')
    search_query = request.GET.get("search")
    page_number = request.GET.get("page", 1)

    private_templates = EmailTemplate.objects.filter(user__id=request.user.id)

    public_templates = EmailTemplate.objects.filter(public=True).order_by('copy_count')

    if public and search_query:
        public_templates = public_templates.filter(Q(subject__icontains=search_query)|Q(name__istartswith=search_query))

    if public == 'True':

        paginator = Paginator(public_templates, per_page=30)
        templates = paginator.get_page(page_number)

        return render(request, 'public-templates.html', context={'templates': templates})

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

    edit = request.GET.get('edit')

    if edit:
        try:
            campaign = EmailCampaign.objects.get(id=edit, user=request.user.id)

            context['campaign'] = campaign

        except EmailCampaign.DoesNotExist:
            return render(request, '404.html')
        
    if request.method == 'POST':

        template = request.POST.get('template')
        email_from = request.POST.get('from_email')
        schedule = request.POST.get('schedule')
        scheduled = request.POST.get('scheduled')

        instance = None

        if edit:
            try:
                instance = EmailCampaign.objects.get(id=edit, user=request.user)

            except (EmailCampaign.DoesNotExist):
                return render(request, '404.html')

        campaign_form = EmailCampaignForm(request.POST or None, request.FILES or None, 
                                            instance=instance)

        followups = json.loads(request.POST.get('followups'))
       
        if campaign_form.is_valid():

            campaign = campaign_form.save(commit=False)
            campaign.user = request.user
            campaign.save()

            # If this is an edit request, update the existing campaign
            if edit:
                EmailCampaignTemplate.objects.filter(campaign=campaign).delete()

            email_form = EmailForm({
                                    'campaign': campaign.id, 
                                    'template': template, 
                                    'email': email_from,
                                    'email_send_rule': EMAIL_SEND_RULES.ALL,
                                    'schedule': schedule,
                                    'scheduled': True if scheduled else False,
                                    'followup': None
                                    })
            print("campaign: ", email_form.is_valid(), email_form.errors)

            if email_form.is_valid():

                main_email = email_form.save(commit=True)

                for i, x in enumerate(followups):
                    follow_up_form = EmailForm({
                                    'campaign': campaign, 
                                    'template': x['followup-template'], 
                                    'email': email_from,
                                    'email_send_rule': x['rule'],
                                    'schedule': x['followup-schedule'],
                                    'scheduled': True if x['followup-scheduled'] != "" else False,
                                    'followup': main_email
                                    })
                    
                    if follow_up_form.is_valid():
                        follow_up_form.save(commit=True)
                    
                    else:
                        campaign.delete()
                        error = follow_up_form.errors.as_data()
                        errors = [f'{list(error[x][0])[0]}' for x in error] 
                        context['error'] = errors
                        print('errors: ', follow_up_form.errors.as_data())

                        break
                
                return redirect('email-campaigns')

            else:
                campaign.delete()
                error = email_form.errors.as_data()
                errors = [f'{list(error[x][0])[0]}' for x in error] 
                context['error'] = errors
                print('errors: ', follow_up_form.errors.as_data())

        else:
            error = campaign_form.errors.as_data()
            errors = [f'{list(error[x][0])[0]}' for x in error] 
            context['error'] = errors
            print('errors: ', follow_up_form.errors.as_data())
            
    return render(request, 'email-campaign-create.html', context)


@login_required
@require_http_methods(['GET'])
def campaigns_view(request):

    view = request.GET.get('view')

    current_datetime = timezone.now()

    first_template_data = EmailCampaign.objects.filter(id=OuterRef('id')  # Correlate with the outer EmailCampaign
                                                                ).order_by('emailcampaigntemplate__schedule').values('emailcampaigntemplate__schedule',  'emailcampaigntemplate__template__subject')[:1]


    campaigns = EmailCampaign.objects.filter(user=request.user.id).annotate(
                                                                        total_templates=Count('emailcampaigntemplate'),
                                                                        completed_templates=Count(
                                                                            'emailcampaigntemplate',
                                                                            filter=Q(emailcampaigntemplate__completed=True)
                                                                        ),
                                                                        all_done=Case(
                                                                            When(
                                                                                total_templates=F('completed_templates'),
                                                                                then=Value(True)
                                                                            ),
                                                                            default=Value(False),
                                                                            output_field=BooleanField()
                                                                        ),
                                                                        first_template_schedule=Subquery(first_template_data.values('emailcampaigntemplate__schedule')),
                                                                        started=Case(
                                                                            When(first_template_schedule__gt=current_datetime, then=Value(True)),
                                                                            default=Value(False),
                                                                            output_field=models.BooleanField()
                                                                        ),
                                                                        subject=Subquery(first_template_data.values('emailcampaigntemplate__template__subject'))
                                                                )

    if view:
        try:
            campaign = campaigns.get(id=view)
          
            return render(request, 'campaign-details.html', context={'campaign': campaign})

        except (EmailCampaign.DoesNotExist):
            return render(request, '404.html')


    return render(request, 'email-campaigns.html', context={
                                                                'campaigns': campaigns,

                                                            })


@login_required
def delete_campaign_view(request, id):
    
    try:
        EmailCampaign.objects.get(user=request.user.id, id=id)
    
    except (EmailCampaign.DoesNotExist):
        return render(request, "404.html")

    return redirect('email-campaigns')



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



# @csrf_exempt
@login_required_rest_api
@require_http_methods(['POST'])
@ratelimit(key='ip', rate='2/min', method=ratelimit.ALL, block=True)
def send_test_mail_view(request):

    # data = json.loads(request.body.decode("utf-8"))

    variables = request.POST.get('variables') or '{}'
    subject = request.POST.get('subject') or ''
    body = request.POST.get('body') or ''
    files = request.FILES.getlist("attachments")

    try:
        variables = json.loads(variables)
    
    except json.JSONDecodeError:
        return JsonResponse({'json': 'invalid variable structure'}, status=400)

    file_size = 0

    for f in files:
        file_size += get_file_size(f)

    if file_size > 10:
        return JsonResponse({'file': 'file attachments size greater than 10 MB'})

    variables['from_name'] = settings.EMAIL_FROM_NAME
    variables['from_signature'] = settings.EMAIL_FROM_SIGNATURE
    variables['from_email'] = settings.EMAIL_FROM

    try:
        
        template = jinja_env.from_string(subject)
        template.render(variables)
    
        template = jinja_env.from_string(body)
        template.render(variables)

    except jinja2.TemplateSyntaxError as e:
        return JsonResponse({'template': f'template syntax error {e}'}, status=400)
    
    try:
        send_email_with_attachments(subject, get_plain_text_from_html(body), body, variables, recipient_list=[request.user.email], attachments=files)

    except Exception as e:
        # print("exceptioin: ", e)
        return JsonResponse({'error': 'something went wrong'}, status=400)

    return JsonResponse({'success': 'the email has been sent'}, status=200)


@require_http_methods(['GET'])
@ratelimit(key='ip', rate='30/min', method=ratelimit.ALL, block=True)
def detailed_template_view(request, id):

    template = EmailTemplate.objects.filter(id=id)

    if not template.exists():
        return JsonResponse({'error': 'does not exist'}, status=404)

    if not template.filter(user=request.user.id).exists():

        if template.filter(public=False):
            return JsonResponse({'error': 'unauthorized'}, status=400)

    email_template = model_to_dict(template.last(), exclude=['copy_count', 'datetime', 'user'])
    print("email: ", email_template)
    return JsonResponse(email_template, status=200)