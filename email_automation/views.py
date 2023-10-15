from django.http import HttpResponseForbidden
from django.shortcuts import render, HttpResponse

from django_ratelimit.exceptions import Ratelimited

def support_view(request):
    return render(request, 'support-opensource.html')


def rate_limiter_view(request, *args, **kwargs):
    return render(request, 'ratelimit.html', status=429)

def view_404(request, *args, **kwargs):
    return render(request, '404.html', status=404)

def handler_403(request, exception=None):
    if isinstance(exception, Ratelimited):
        return HttpResponse('Sorry you are blocked', status=429)
    return HttpResponseForbidden('Forbidden')