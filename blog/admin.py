from django.contrib import admin
from django.urls import reverse
from django.template.defaultfilters import slugify
from django.conf import settings

from . import models


class InlineBlogImgAdmin(admin.StackedInline):

    model = models.Images
    extra = 0

class InlineRelatedBlogAdmin(admin.StackedInline):

    model = models.RelatedBlog
    fk_name = 'blog'

    extra = 0


@admin.register(models.Blog)
class BlogAdmin(admin.ModelAdmin):

    list_display = ['id', 'ordering', 'title', 'datetime', 'link', 'removed']
    search_fields = ['title', 'ordering']

    ordering = ['ordering']
    list_editable = ['ordering', 'removed']
    # readonly_fields = ['blog']
    list_filter = ['datetime', 'removed']
    
    inlines = [InlineRelatedBlogAdmin, InlineBlogImgAdmin]

    def link(self, obj):
     
        return settings.DOMAIN+reverse(f"blog-view", kwargs={"id": obj.id, "title":slugify(obj.title)})


@admin.register(models.Images)
class BlogImageAdmin(admin.ModelAdmin):

    list_display = ['id', 'blog', 'img']
    autocomplete_fields = ['blog']


@admin.register(models.RelatedBlog)
class RelatedBlogAdmin(admin.ModelAdmin):

    list_display = ['id', 'blog', 'related_blog']
    

@admin.register(models.FAQ)
class FAQAdmin(admin.ModelAdmin):

    list_display = ['id', 'question']
    