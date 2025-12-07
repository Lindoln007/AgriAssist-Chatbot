"""
Admin interface for settings models
"""
from django.contrib import admin
from .models import SettingCategory, UserSetting, SystemSetting, SettingOption


@admin.register(SettingCategory)
class SettingCategoryAdmin(admin.ModelAdmin):
    list_display = ('display_name', 'name', 'order', 'is_user_visible', 'is_admin_only')
    list_filter = ('is_user_visible', 'is_admin_only')
    search_fields = ('name', 'display_name')
    ordering = ('order', 'name')


class SettingOptionInline(admin.TabularInline):
    model = SettingOption
    extra = 1
    fields = ('value', 'display_name', 'order')


@admin.register(UserSetting)
class UserSettingAdmin(admin.ModelAdmin):
    list_display = ('display_name', 'user', 'key', 'setting_type', 'category', 'is_visible', 'updated_at')
    list_filter = ('setting_type', 'category', 'is_visible', 'created_at')
    search_fields = ('key', 'display_name', 'user__username')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [SettingOptionInline]
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'key', 'display_name', 'description', 'category')
        }),
        ('Setting Details', {
            'fields': ('setting_type', 'value', 'is_visible', 'order')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(SystemSetting)
class SystemSettingAdmin(admin.ModelAdmin):
    list_display = ('display_name', 'key', 'setting_type', 'category', 'updated_at', 'updated_by')
    list_filter = ('setting_type', 'category', 'created_at')
    search_fields = ('key', 'display_name')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [SettingOptionInline]
    fieldsets = (
        ('Basic Information', {
            'fields': ('key', 'display_name', 'description', 'category')
        }),
        ('Setting Details', {
            'fields': ('setting_type', 'value', 'order')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'updated_by'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if change:
            obj.updated_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(SettingOption)
class SettingOptionAdmin(admin.ModelAdmin):
    list_display = ('display_name', 'value', 'setting', 'system_setting', 'order')
    list_filter = ('order',)
    search_fields = ('value', 'display_name')
