from django.contrib import admin

# Register your models here.
from .models import Terms


@admin.register(Terms)
class TandCAdmin(admin.ModelAdmin):

    list_display = ['id', 'datetime', 'info_type']