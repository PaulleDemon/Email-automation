from urllib.parse import urlparse
from django.conf import settings
from django.db import models
from django.core.exceptions import ValidationError

from utils import constraint_fields


def next_number():

    if not Blog.objects.exists():
        return None

    return Blog.objects.order_by('ordering').last().ordering + 1


class BLOG_TYPE(models.IntegerChoices):

    BLOG = (0, 'blog')
    PRIVACY = (1, 'privacy')
    T_AND_C = (2, 't&c')
    

class Blog(models.Model):

    ordering = models.IntegerField(unique=True, default=next_number)
    title = models.CharField(max_length=250)
    description = models.TextField()
    datetime = models.DateTimeField(auto_now=True)

    blog_type = models.PositiveSmallIntegerField(choices=BLOG_TYPE.choices, default=BLOG_TYPE.BLOG)

    removed = models.BooleanField(default=False)

    class Meta:

        verbose_name = 'blog'
        verbose_name_plural = 'blogs'
    
    def __str__(self):
        return self.title


class Images(models.Model):

    blog = models.ForeignKey(Blog, on_delete=models.CASCADE)
    img = constraint_fields.ContentTypeRestrictedFileField(upload_to='blog-media/', null=True, blank=True, max_upload_size=5242880, content_types=["image/jpeg", "image/png", "image/jpg"])

    class Meta:

        verbose_name = 'blog media'
        verbose_name_plural = 'blog media'


class RelatedBlog(models.Model):

    blog = models.ForeignKey(Blog, on_delete=models.CASCADE)
    related_blog = models.ForeignKey(Blog, on_delete=models.CASCADE, related_name='related_blog')

    class Meta:

        verbose_name = 'related blog'
        verbose_name_plural = 'related blogs'

    def __str__(self):
        return self.blog.title


class FAQ(models.Model):

    question = models.TextField()
    answer = models.TextField() 

    def __str__(self) -> str:
        return f'{self.question}'