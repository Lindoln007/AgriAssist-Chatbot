from django.contrib import admin
from .models import GovUpdate, UserUpdateView

@admin.register(GovUpdate)
class GovUpdateAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'date_posted', 'created_by', 'created_at')
    list_filter = ('category', 'date_posted', 'created_by')
    search_fields = ('title', 'content')
    date_hierarchy = 'date_posted'
    ordering = ('-date_posted', '-created_at')
    
    fieldsets = (
        ('Update Information', {
            'fields': ('title', 'category', 'date_posted')
        }),
        ('Content', {
            'fields': ('content', 'file')
        }),
        ('Metadata', {
            'fields': ('created_by',),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if not change:  # If creating new object
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(UserUpdateView)
class UserUpdateViewAdmin(admin.ModelAdmin):
    list_display = ('user', 'update', 'viewed_at')
    list_filter = ('viewed_at', 'user')
    search_fields = ('user__username', 'update__title')
    date_hierarchy = 'viewed_at'
    ordering = ('-viewed_at',)
    readonly_fields = ('viewed_at',)
