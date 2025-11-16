from django.contrib import admin
from .models import AgriculturalFAQ, PestInfo, FertilizerGuideline, CropManagementTip, ExtensionResource

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
