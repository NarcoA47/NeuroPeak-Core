from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, LecturerProfile, StudentProfile
from django.utils.translation import gettext_lazy as _

class CustomUserAdmin(UserAdmin):
    # The forms to add and change user instances
    list_display = ('email', 'first_name', 'last_name', 'user_type', 'is_staff')
    list_filter = ('user_type', 'is_staff', 'is_superuser', 'is_active')
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name')}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
        (_('User Type'), {'fields': ('user_type',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'user_type'),
        }),
    )
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)
    filter_horizontal = ('groups', 'user_permissions',)

class LecturerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'department', 'specialization')
    search_fields = ('user__email', 'user__first_name', 'user__last_name', 'department')
    raw_id_fields = ('user',)
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(user=request.user)

class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'program', 'year_of_study')
    search_fields = ('user__email', 'user__first_name', 'user__last_name')
    list_filter = ('program', 'year_of_study')
    raw_id_fields = ('user',)
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(user=request.user)

# Register your models here
admin.site.register(User, CustomUserAdmin)
admin.site.register(LecturerProfile, LecturerProfileAdmin)
admin.site.register(StudentProfile, StudentProfileAdmin)