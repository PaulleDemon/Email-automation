from django.shortcuts import render

from .models import TERMS_TYPE, Terms
# Create your views here.

def t_and_c_view(request):

    terms = Terms.objects.filter(info_type=TERMS_TYPE.T_AND_C).last()

    return render(request, 'terms.html', {'terms': terms})


def privacy_view(request):
    terms = Terms.objects.filter(info_type=TERMS_TYPE.PRIVACY).last()

    return render(request, 'terms.html', {'terms': terms})
