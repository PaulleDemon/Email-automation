from itertools import zip_longest

from django.http import Http404
from django.shortcuts import render
from django.core.paginator import Paginator

from . import models


def blog_list(request): 

    search_query = request.GET.get("search")
    page_number = request.GET.get("page", 1)

    faq = []

    if search_query:
        blogs = models.Blog.objects.filter(title__icontains=search_query, blog_type=models.BLOG_TYPE.BLOG).order_by('ordering')

    else:
        blogs = models.Blog.objects.filter(blog_type=models.BLOG_TYPE.BLOG).order_by('ordering')

        faq = models.FAQ.objects.all()

    blogs = blogs.exclude(removed=True)

    paginator = Paginator(blogs, per_page=10)
    blog_objects = paginator.get_page(page_number)

    blog_data = []


    for x in blog_objects:
        image = models.Images.objects.filter(blog=x.id)

        data = {
            'id': x.id,
            'title': x.title,
        }

        if image.exists():
            data['image'] = image.last().img
        
        blog_data.append(data)

    
    return render(request, "blog-list.html", {"blogs": blog_data, 
                                              'search_query': '' if search_query is None else search_query, 
                                              'page_title': 'Blogs',
                                              'page': blog_objects,
                                              'faq': faq
                                              })



def blog_detail(request, id, title=""):

    try:
        blog = models.Blog.objects.exclude(removed=True).prefetch_related('relatedblog_set', 'images_set').get(id=id)
    
    except models.Blog.DoesNotExist:
        raise Http404

    return render(request, 'blog.html', {'blog': blog, 'page_title': f'blog | {blog.title}'})


def t_and_c_view(request):

    terms = models.Blog.objects.filter(blog_type=models.BLOG_TYPE.T_AND_C).last()

    return render(request, 'terms.html', {'terms': terms})


def privacy_view(request):
    terms = models.Blog.objects.filter(blog_type=models.BLOG_TYPE.PRIVACY).last()

    return render(request, 'terms.html', {'terms': terms})
