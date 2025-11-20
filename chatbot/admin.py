from django.contrib import admin
from .models import (
    AgriculturalFAQ, PestInfo, FertilizerGuideline, CropManagementTip, 
    ExtensionResource, UserProfile, ChatSession, ChatMessage
)

@admin.register(AgriculturalFAQ)
class AgriculturalFAQAdmin(admin.ModelAdmin):
    list_display = ('question', 'category', 'created_at')
    search_fields = ('question', 'answer', 'category')

@admin.register(PestInfo)
class PestInfoAdmin(admin.ModelAdmin):
    list_display = ('name', 'category')
    search_fields = ('name', 'description', 'symptoms')

@admin.register(FertilizerGuideline)
class FertilizerGuidelineAdmin(admin.ModelAdmin):
    list_display = ('crop_type', 'fertilizer_type', 'application_rate')
    search_fields = ('crop_type', 'fertilizer_type')

@admin.register(CropManagementTip)
class CropManagementTipAdmin(admin.ModelAdmin):
    list_display = ('crop_type', 'tip_title', 'season')
    search_fields = ('crop_type', 'tip_title', 'tip_content')

@admin.register(ExtensionResource)
class ExtensionResourceAdmin(admin.ModelAdmin):
    list_display = ('title', 'resource_type', 'created_at')
    search_fields = ('title', 'content')

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'display_name', 'location', 'specialization', 'created_at')
    search_fields = ('user__username', 'display_name', 'location', 'specialization')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'title', 'created_at', 'updated_at')
    search_fields = ('user__username', 'title')
    list_filter = ('created_at', 'user')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'session', 'user_message_preview', 'created_at')
    search_fields = ('session__id', 'user_message', 'bot_response', 'session__user__username')
    list_filter = ('created_at', 'session__user')
    readonly_fields = ('created_at',)
    
    def user_message_preview(self, obj):
        """Show first 50 characters of user message"""
        return obj.user_message[:50] + ('...' if len(obj.user_message) > 50 else '')
    user_message_preview.short_description = 'User Message'
