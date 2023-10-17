from django.urls import path
from django.shortcuts import redirect

from . import views

urlpatterns = [
     
    path('', lambda _: redirect("blog-list")),
    path('list/', views.blog_list, name="blog-list"),
    path('<int:id>/<slug:title>/', views.blog_detail, name="blog-view"),
    
    path('<int:id>/<slug:title>/', views.blog_detail, name="blog-view"),
    
    path('terms-and-conditions/', views.t_and_c_view, name='t&c'),
    path('privacy/', views.privacy_view, name='privacy')

]
