from django.shortcuts import render


def support_view(request):
    return render(request, 'support-opensource.html')


def rate_limiter_view(request, *args, **kwargs):
    return render(request, 'ratelimit.html')