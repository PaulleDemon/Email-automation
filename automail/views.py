from django.shortcuts import render


def email_automation(request):
    return render(request, 'email-automation.html')



