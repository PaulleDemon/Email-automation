from django.conf import settings  # Import the Django settings module
from django.shortcuts import redirect


def login_required_for_post(function, login_url=settings.LOGIN_URL):
    
    def wrapper_func(request, *args, **kwargs):
        if request.method == 'POST' and not request.user.is_authenticated:
            return redirect(login_url)

        return function(request, *args, **kwargs)

    return wrapper_func
