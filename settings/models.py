"""
Settings models for user and system-level customization.
Flexible structure allows adding new settings without breaking existing code.
"""
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


class SettingCategory(models.Model):
    """Categories for organizing settings"""
    name = models.CharField(max_length=100, unique=True)
    display_name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, default='fas fa-cog', help_text='Font Awesome icon class')
    order = models.IntegerField(default=0, help_text='Display order')
    is_user_visible = models.BooleanField(default=True, help_text='Visible to regular users')
    is_admin_only = models.BooleanField(default=False, help_text='Only visible to admins')
    
    class Meta:
        verbose_name_plural = 'Setting Categories'
        ordering = ['order', 'name']
    
    def __str__(self):
        return self.display_name


class UserSetting(models.Model):
    """User-specific settings"""
    SETTING_TYPES = [
        ('string', 'Text'),
        ('integer', 'Number'),
        ('boolean', 'True/False'),
        ('choice', 'Select Option'),
        ('json', 'JSON Data'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_settings')
    key = models.CharField(max_length=100, db_index=True)
    value = models.TextField(blank=True)
    setting_type = models.CharField(max_length=20, choices=SETTING_TYPES, default='string')
    category = models.ForeignKey(SettingCategory, on_delete=models.SET_NULL, null=True, blank=True)
    display_name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    is_visible = models.BooleanField(default=True)
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user', 'key']
        ordering = ['category__order', 'order', 'display_name']
        indexes = [
            models.Index(fields=['user', 'key']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.display_name}"
    
    def get_value(self):
        """Get typed value based on setting_type"""
        if self.setting_type == 'boolean':
            return self.value.lower() in ('true', '1', 'yes', 'on')
        elif self.setting_type == 'integer':
            try:
                return int(self.value)
            except (ValueError, TypeError):
                return 0
        elif self.setting_type == 'json':
            import json
            try:
                return json.loads(self.value)
            except (ValueError, TypeError):
                return {}
        return self.value
    
    def set_value(self, value):
        """Set value with proper type conversion"""
        if self.setting_type == 'boolean':
            self.value = 'true' if bool(value) else 'false'
        elif self.setting_type == 'integer':
            self.value = str(int(value))
        elif self.setting_type == 'json':
            import json
            self.value = json.dumps(value)
        else:
            self.value = str(value)


class SystemSetting(models.Model):
    """System-level settings (admin only)"""
    SETTING_TYPES = [
        ('string', 'Text'),
        ('integer', 'Number'),
        ('boolean', 'True/False'),
        ('choice', 'Select Option'),
        ('json', 'JSON Data'),
    ]
    
    key = models.CharField(max_length=100, unique=True, db_index=True)
    value = models.TextField(blank=True)
    setting_type = models.CharField(max_length=20, choices=SETTING_TYPES, default='string')
    category = models.ForeignKey(SettingCategory, on_delete=models.SET_NULL, null=True, blank=True)
    display_name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='system_settings_updated')
    
    class Meta:
        ordering = ['category__order', 'order', 'display_name']
    
    def __str__(self):
        return self.display_name
    
    def get_value(self):
        """Get typed value based on setting_type"""
        if self.setting_type == 'boolean':
            return self.value.lower() in ('true', '1', 'yes', 'on')
        elif self.setting_type == 'integer':
            try:
                return int(self.value)
            except (ValueError, TypeError):
                return 0
        elif self.setting_type == 'json':
            import json
            try:
                return json.loads(self.value)
            except (ValueError, TypeError):
                return {}
        return self.value
    
    def set_value(self, value):
        """Set value with proper type conversion"""
        if self.setting_type == 'boolean':
            self.value = 'true' if bool(value) else 'false'
        elif self.setting_type == 'integer':
            self.value = str(int(value))
        elif self.setting_type == 'json':
            import json
            self.value = json.dumps(value)
        else:
            self.value = str(value)


class SettingOption(models.Model):
    """Options for choice-type settings"""
    setting = models.ForeignKey(UserSetting, on_delete=models.CASCADE, related_name='options', null=True, blank=True)
    system_setting = models.ForeignKey(SystemSetting, on_delete=models.CASCADE, related_name='options', null=True, blank=True)
    value = models.CharField(max_length=200)
    display_name = models.CharField(max_length=200)
    order = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['order', 'display_name']
        constraints = [
            models.CheckConstraint(
                check=(models.Q(setting__isnull=False) & models.Q(system_setting__isnull=True)) |
                      (models.Q(setting__isnull=True) & models.Q(system_setting__isnull=False)),
                name='one_setting_required'
            )
        ]
    
    def __str__(self):
        return f"{self.display_name} ({self.value})"
