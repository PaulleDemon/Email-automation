from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserCreationForm, UserChangeForm

from django.contrib.auth.models import Group

from .models import User
from .admingroupform import GroupAdminForm

# Unregister the original Group admin.
admin.site.unregister(Group)

# Create a new Group admin.
class GroupAdmin(admin.ModelAdmin):
    # Use our custom form.
    form = GroupAdminForm
    # Filter permissions horizontal as well.
    filter_horizontal = ['permissions']

# Register the new Group ModelAdmin.
admin.site.register(Group, GroupAdmin)


class CustomUserCreationForm(UserCreationForm):

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ()


class CustomUserChangeForm(UserChangeForm):

    class Meta(UserChangeForm.Meta):
        model = User
        # fields = ('name', )


@admin.register(User)
class UserAdmin(UserAdmin):

    form = CustomUserChangeForm
    add_form = CustomUserCreationForm

    list_display = ['id', 'name',  'email', 'is_active']
    list_filter = ['date_joined', 'is_active', 'is_admin']

    ordering = ['-date_joined']
    readonly_fields = ['date_joined']

    fieldsets = (
        ('user details', {'fields': ('id', 'email', 'name',   
                                    'date_joined', 
                                    'ip_address', 'password')}), # displays hashed password
        ('permissions', {'fields': ('is_staff', 'is_active', 'is_admin')}),
        ('authorization groups', {'fields': ('groups', )}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2')}
        ),
    )
    list_editable = ['is_active',]
    search_fields = ['name', 'email']

    readonly_fields = ['id', 'date_joined']
    
