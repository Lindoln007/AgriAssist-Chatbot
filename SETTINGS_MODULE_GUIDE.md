# Settings Module - Complete Guide

## Overview

The Settings module is a fully integrated, auto-populated customization system that provides role-based settings directly within the chatbot interface. It **never shows an empty screen** and automatically creates default settings for all users.

## Key Features

### ✅ Auto-Population
- **No empty screens**: Settings are automatically created when users first access the module
- **Default settings**: Every user gets a complete set of personal customization options immediately
- **Admin settings**: System-level settings are automatically available to administrators
- **No pre-configuration needed**: Works out of the box without manual setup

### ✅ Role-Based Access
- **Regular Users**: See personal preferences, chatbot settings, and notification options
- **Administrators**: See all user settings PLUS system-level configuration options
- **Automatic detection**: User role is detected automatically, no manual configuration

### ✅ Fully Integrated
- **Chatbot integration**: Accessible directly from the chatbot page via settings icon
- **Modal interface**: Opens as an overlay without leaving the chatbot
- **Real-time updates**: Changes apply immediately with visual feedback

## Default Settings

### Personal Preferences (All Users)
1. **Theme** - Choose Light, Dark, or Auto (System)
2. **Show Chat History** - Toggle sidebar chat history display

### Chatbot Settings (All Users)
1. **Response Style** - Concise, Balanced, or Detailed responses
2. **Enable Weather Integration** - Include weather data in responses
3. **Auto-save Conversations** - Automatically save all conversations

### Notifications (All Users)
1. **Email Notifications** - Receive email notifications
2. **Reminder Notifications** - Get notified about farm reminders
3. **Policy Update Notifications** - Notify about new government updates

### System Settings (Admin Only)
1. **Max Chat Sessions per User** - Limit number of sessions
2. **Session Retention (Days)** - Auto-delete old sessions
3. **Enable Public API** - Allow external API access
4. **API Rate Limit** - Requests per minute limit
5. **Maintenance Mode** - Restrict access to admins only
6. **Auto-backup Enabled** - Daily database backups

## How It Works

### Automatic Creation
1. **On User Creation**: When a new user signs up, default settings are automatically created via Django signals
2. **On First Access**: When a user opens settings for the first time, defaults are created if missing
3. **For Existing Users**: Run `python manage.py init_default_settings` to initialize settings

### Dynamic Updates
- New settings added through Django admin automatically appear in the interface
- Settings are organized by categories with icons
- Changes save immediately via AJAX
- Success notifications confirm updates

## Usage

### For Users
1. Click the **Settings icon** (⚙️) in the chatbot header
2. Settings modal opens with all available options
3. Modify any setting and click **Save**
4. Changes apply immediately

### For Administrators
1. Access settings the same way as regular users
2. Additional **System Settings** section appears
3. System settings are marked with "SYSTEM" badge
4. Changes affect the entire platform

### For Developers
1. Add new settings via Django admin (`/admin/settings/`)
2. Settings automatically appear in the interface based on:
   - User role (user vs admin)
   - Category visibility settings
   - Setting visibility flags

## Management Commands

### Initialize Settings for All Users
```bash
python manage.py init_default_settings
```

### Initialize Settings for Specific User
```bash
python manage.py init_default_settings --user username
```

## Adding New Settings

### Via Django Admin
1. Go to `/admin/settings/`
2. Create a new `SettingCategory` (if needed)
3. Create `UserSetting` or `SystemSetting` entries
4. Settings automatically appear in the chatbot interface

### Programmatically
```python
from settings.utils import ensure_user_default_settings, ensure_system_default_settings
from django.contrib.auth.models import User

# For a user
user = User.objects.get(username='example')
ensure_user_default_settings(user)

# For system (admin only)
ensure_system_default_settings()
```

## Technical Details

### Files Structure
```
settings/
├── models.py          # SettingCategory, UserSetting, SystemSetting, SettingOption
├── views.py           # Settings views with auto-creation
├── utils.py           # Default settings creation functions
├── signals.py         # Auto-create settings on user creation
├── admin.py           # Django admin interface
├── urls.py            # URL routing
└── management/
    └── commands/
        └── init_default_settings.py  # Management command
```

### Auto-Creation Flow
1. User accesses settings → `settings_index()` view called
2. View calls `ensure_all_default_settings(user)`
3. Function checks and creates missing default settings
4. Settings returned to user interface
5. User sees populated settings immediately

### Settings Types
- **boolean**: Toggle switch (on/off)
- **string**: Text input
- **integer**: Number input
- **choice**: Dropdown with options
- **json**: JSON data (for complex settings)

## Best Practices

1. **Always use defaults**: Never show empty settings screens
2. **Organize by category**: Group related settings together
3. **Clear descriptions**: Help users understand each setting
4. **Role-appropriate**: Only show settings users can actually use
5. **Immediate feedback**: Show success/error messages for all actions

## Troubleshooting

### Settings Not Appearing
- Run `python manage.py init_default_settings` to create defaults
- Check that settings have `is_visible=True` for user settings
- Verify category `is_user_visible` or `is_admin_only` flags

### Settings Not Saving
- Check browser console for JavaScript errors
- Verify CSRF token is included in requests
- Check Django admin for setting existence

### Empty Settings Screen
- This should never happen! If it does:
  1. Run `python manage.py init_default_settings`
  2. Check that `ensure_all_default_settings()` is called in views
  3. Verify user has proper permissions

## Future Enhancements

The module is designed to be extensible:
- Add new setting types easily
- Create custom setting categories
- Add setting validation rules
- Implement setting dependencies
- Add bulk setting operations

---

**Status**: ✅ Fully Functional - Auto-populated, role-based, integrated settings module

