
from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),


    path('', include('automail.urls')),
    path('user/', include('user.urls')),
    
    path('email/', include('automail.urls')),
    
    path("__reload__/", include("django_browser_reload.urls")),

]

urlpatterns += static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
