
from django.contrib import admin
from django.conf import settings
from django.shortcuts import redirect
from django.conf.urls.static import static
from django.urls import path, include, re_path

from .views import (support_view, rate_limiter_view, view_404, 
                        handler_403, home_view)

handler404 = view_404

handler403 = handler_403



urlpatterns = [
    path('admin/', admin.site.urls),

    path('support/', support_view, name='support-view'),
    path('ratelimit-error/', rate_limiter_view, name='ratelimit-error'),

    path('', home_view),
    path('user/', include('user.urls')),
    path('terms/', include('terms.urls')),
    
    path('email/', include('automail.urls')),
    path("__reload__/", include("django_browser_reload.urls")),
    
    re_path(r'^.*/$', view_404, name='page_not_found'),
]
if settings.DEBUG:
   urlpatterns +=  []

urlpatterns += static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
