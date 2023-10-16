from django.urls import path

from .views import t_and_c_view, privacy_view

urlpatterns = [
    path('', t_and_c_view, name='t&c'),
    path('privacy/', privacy_view, name='privacy')
]
