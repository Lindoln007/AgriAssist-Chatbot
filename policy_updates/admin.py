from django.contrib import admin
from .models import GovUpdate

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
