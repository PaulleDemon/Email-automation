from django.shortcuts import render
from django.views.decorators.http import require_http_methods


@require_http_methods(['GET', 'POST'])
def email_template_create(request):
   
    if request.method == 'GET':
        return render(request, 'email-template-create.html')
    
    return render(request, 'email-template-create.html')


@require_http_methods(['GET'])
def email_templates(request):
    
    return render(request, 'email-templates.html')




