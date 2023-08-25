from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserCreationForm, UserChangeForm

from core.models.user.user_model import CustomUser


READABLE_FIELDS = ['id', 'username', 'is_admin', 'is_active', 'registered_at', 'last_activity_at']
WRITABLE_FIELDS = ['username', 'is_admin', 'is_active', 'last_activity_at']


class CustomUserCreationForm(UserCreationForm):

    class Meta(UserCreationForm):
        model = CustomUser
        fields = WRITABLE_FIELDS


class CustomUserChangeForm(UserChangeForm):

    class Meta:
        model = CustomUser
        fields = WRITABLE_FIELDS


class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = READABLE_FIELDS
    list_filter = READABLE_FIELDS
    fieldsets = [
        [None, {'fields': ['id']}],
        ['Permissions', {'fields': ['is_admin', 'is_active']}],
    ]
    add_fieldsets = [
        [
            None,
            {
                'classes': ['wide'],
                'fields': ['username', 'password1', 'password2', 'is_admin', 'is_active']
            }
        ],
    ]
    search_fields = ['username']
    ordering = ['username']
