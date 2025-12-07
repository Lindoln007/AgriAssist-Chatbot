"""
Utility functions for auto-creating default settings
"""
from django.contrib.auth.models import User
from .models import SettingCategory, UserSetting, SystemSetting, SettingOption


def get_or_create_default_categories():
    """Get or create default setting categories"""
    categories = {}
    
    # Personal Preferences Category
    personal_cat, _ = SettingCategory.objects.get_or_create(
        name='personal',
        defaults={
            'display_name': 'Personal Preferences',
            'description': 'Customize your personal experience',
            'icon': 'fas fa-user',
            'order': 1,
            'is_user_visible': True,
            'is_admin_only': False,
        }
    )
    categories['personal'] = personal_cat
    
    # Chatbot Settings Category
    chatbot_cat, _ = SettingCategory.objects.get_or_create(
        name='chatbot',
        defaults={
            'display_name': 'Chatbot Settings',
            'description': 'Configure chatbot behavior and responses',
            'icon': 'fas fa-robot',
            'order': 2,
            'is_user_visible': True,
            'is_admin_only': False,
        }
    )
    categories['chatbot'] = chatbot_cat
    
    # Notifications Category
    notifications_cat, _ = SettingCategory.objects.get_or_create(
        name='notifications',
        defaults={
            'display_name': 'Notifications',
            'description': 'Manage your notification preferences',
            'icon': 'fas fa-bell',
            'order': 3,
            'is_user_visible': True,
            'is_admin_only': False,
        }
    )
    categories['notifications'] = notifications_cat
    
    # System Settings Category (Admin only)
    system_cat, _ = SettingCategory.objects.get_or_create(
        name='system',
        defaults={
            'display_name': 'System Settings',
            'description': 'System-wide configuration options',
            'icon': 'fas fa-server',
            'order': 10,
            'is_user_visible': False,
            'is_admin_only': True,
        }
    )
    categories['system'] = system_cat
    
    return categories


def ensure_user_default_settings(user):
    """Ensure a user has all default personal settings"""
    categories = get_or_create_default_categories()
    
    # Theme Preference
    UserSetting.objects.get_or_create(
        user=user,
        key='theme_preference',
        defaults={
            'setting_type': 'choice',
            'category': categories['personal'],
            'display_name': 'Theme',
            'description': 'Choose your preferred color theme',
            'value': 'auto',
            'is_visible': True,
            'order': 1,
        }
    )
    setting = UserSetting.objects.get(user=user, key='theme_preference')
    if not setting.options.exists():
        SettingOption.objects.get_or_create(setting=setting, value='light', defaults={'display_name': 'Light', 'order': 1})
        SettingOption.objects.get_or_create(setting=setting, value='dark', defaults={'display_name': 'Dark', 'order': 2})
        SettingOption.objects.get_or_create(setting=setting, value='auto', defaults={'display_name': 'Auto (System)', 'order': 3})
    
    # Show Chat History
    UserSetting.objects.get_or_create(
        user=user,
        key='show_chat_history',
        defaults={
            'setting_type': 'boolean',
            'category': categories['personal'],
            'display_name': 'Show Chat History',
            'description': 'Display previous chat sessions in sidebar',
            'value': 'true',
            'is_visible': True,
            'order': 2,
        }
    )
    
    # Chatbot Response Style
    UserSetting.objects.get_or_create(
        user=user,
        key='response_style',
        defaults={
            'setting_type': 'choice',
            'category': categories['chatbot'],
            'display_name': 'Response Style',
            'description': 'How detailed should chatbot responses be?',
            'value': 'balanced',
            'is_visible': True,
            'order': 1,
        }
    )
    setting = UserSetting.objects.get(user=user, key='response_style')
    if not setting.options.exists():
        SettingOption.objects.get_or_create(setting=setting, value='concise', defaults={'display_name': 'Concise', 'order': 1})
        SettingOption.objects.get_or_create(setting=setting, value='balanced', defaults={'display_name': 'Balanced', 'order': 2})
        SettingOption.objects.get_or_create(setting=setting, value='detailed', defaults={'display_name': 'Detailed', 'order': 3})
    
    # Enable Weather Integration
    UserSetting.objects.get_or_create(
        user=user,
        key='enable_weather',
        defaults={
            'setting_type': 'boolean',
            'category': categories['chatbot'],
            'display_name': 'Enable Weather Integration',
            'description': 'Include weather data in chatbot responses when relevant',
            'value': 'true',
            'is_visible': True,
            'order': 2,
        }
    )
    
    # Auto-save Conversations
    UserSetting.objects.get_or_create(
        user=user,
        key='auto_save_conversations',
        defaults={
            'setting_type': 'boolean',
            'category': categories['chatbot'],
            'display_name': 'Auto-save Conversations',
            'description': 'Automatically save all conversations',
            'value': 'true',
            'is_visible': True,
            'order': 3,
        }
    )
    
    # Email Notifications
    UserSetting.objects.get_or_create(
        user=user,
        key='email_notifications',
        defaults={
            'setting_type': 'boolean',
            'category': categories['notifications'],
            'display_name': 'Email Notifications',
            'description': 'Receive email notifications for reminders and updates',
            'value': 'true',
            'is_visible': True,
            'order': 1,
        }
    )
    
    # Reminder Notifications
    UserSetting.objects.get_or_create(
        user=user,
        key='reminder_notifications',
        defaults={
            'setting_type': 'boolean',
            'category': categories['notifications'],
            'display_name': 'Reminder Notifications',
            'description': 'Get notified about upcoming farm reminders',
            'value': 'true',
            'is_visible': True,
            'order': 2,
        }
    )
    
    # Policy Update Notifications
    UserSetting.objects.get_or_create(
        user=user,
        key='policy_update_notifications',
        defaults={
            'setting_type': 'boolean',
            'category': categories['notifications'],
            'display_name': 'Policy Update Notifications',
            'description': 'Notify me when new government updates are posted',
            'value': 'true',
            'is_visible': True,
            'order': 3,
        }
    )


def ensure_system_default_settings():
    """Ensure system has all default admin settings"""
    categories = get_or_create_default_categories()
    
    # Max Chat Sessions per User
    SystemSetting.objects.get_or_create(
        key='max_chat_sessions',
        defaults={
            'setting_type': 'integer',
            'category': categories['system'],
            'display_name': 'Max Chat Sessions per User',
            'description': 'Maximum number of chat sessions a user can have',
            'value': '50',
            'order': 1,
        }
    )
    
    # Chat Session Retention Days
    SystemSetting.objects.get_or_create(
        key='session_retention_days',
        defaults={
            'setting_type': 'integer',
            'category': categories['system'],
            'display_name': 'Session Retention (Days)',
            'description': 'Number of days to keep chat sessions before auto-deletion',
            'value': '90',
            'order': 2,
        }
    )
    
    # Enable Public API
    SystemSetting.objects.get_or_create(
        key='enable_public_api',
        defaults={
            'setting_type': 'boolean',
            'category': categories['system'],
            'display_name': 'Enable Public API',
            'description': 'Allow external access to chatbot API',
            'value': 'false',
            'order': 3,
        }
    )
    
    # API Rate Limit
    SystemSetting.objects.get_or_create(
        key='api_rate_limit',
        defaults={
            'setting_type': 'integer',
            'category': categories['system'],
            'display_name': 'API Rate Limit (per minute)',
            'description': 'Maximum API requests allowed per user per minute',
            'value': '60',
            'order': 4,
        }
    )
    
    # Maintenance Mode
    SystemSetting.objects.get_or_create(
        key='maintenance_mode',
        defaults={
            'setting_type': 'boolean',
            'category': categories['system'],
            'display_name': 'Maintenance Mode',
            'description': 'Enable maintenance mode (restricts access to admins only)',
            'value': 'false',
            'order': 5,
        }
    )
    
    # Auto-backup Enabled
    SystemSetting.objects.get_or_create(
        key='auto_backup_enabled',
        defaults={
            'setting_type': 'boolean',
            'category': categories['system'],
            'display_name': 'Auto-backup Enabled',
            'description': 'Automatically backup database daily',
            'value': 'true',
            'order': 6,
        }
    )


def ensure_all_default_settings(user):
    """Ensure all default settings exist for a user and system"""
    ensure_user_default_settings(user)
    if user.is_staff or user.is_superuser:
        ensure_system_default_settings()

