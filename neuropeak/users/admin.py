from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django import forms
from .models import User, LecturerProfile, StudentProfile
from django.utils.translation import gettext_lazy as _

class UserChangeForm(forms.ModelForm):
    class Meta:
        model = User
        fields = '__all__'

class CustomUserAdmin(BaseUserAdmin):
    form = UserChangeForm
    model = User
    list_display = ('email', 'first_name', 'last_name', 'user_type', 'is_staff')
    list_filter = ('user_type', 'is_staff', 'is_superuser', 'is_active')
    fieldsets = (
        (None, {'fields': ('email', 'password', 'user_type')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name')}),
        (_('Lecturer info'), {'fields': ('department', 'specialization', 'bio')}),
        (_('Student info'), {'fields': ('program', 'year_of_study')}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'user_type', 'first_name', 'last_name', 'department', 'specialization', 'bio', 'program', 'year_of_study', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}
        ),
    )
    search_fields = ('email',)
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