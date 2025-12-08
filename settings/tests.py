"""
Comprehensive test suite for the settings app.
Tests models, views, auto-population, and role-based access.
"""
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from .models import SettingCategory, UserSetting, SystemSetting, SettingOption
from .utils import ensure_all_default_settings, ensure_user_default_settings, ensure_system_default_settings


class SettingCategoryModelTest(TestCase):
    """Test SettingCategory model"""
    
    def test_category_creation(self):
        """Test SettingCategory creation"""
        category = SettingCategory.objects.create(
            name='test_category',
            display_name='Test Category',
            description='Test description',
            icon='fas fa-test',
            order=1,
            is_user_visible=True,
            is_admin_only=False
        )
        self.assertEqual(category.name, 'test_category')
        self.assertEqual(category.display_name, 'Test Category')
        self.assertTrue(category.is_user_visible)
        self.assertFalse(category.is_admin_only)


class UserSettingModelTest(TestCase):
    """Test UserSetting model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        # Get or create category (may already exist from default creation)
        self.category, _ = SettingCategory.objects.get_or_create(
            name='test_personal',
            defaults={
                'display_name': 'Test Personal',
                'is_user_visible': True
            }
        )
    
    def test_user_setting_creation(self):
        """Test UserSetting creation"""
        setting = UserSetting.objects.create(
            user=self.user,
            key='test_setting',
            value='test_value',
            setting_type='string',
            category=self.category,
            display_name='Test Setting',
            is_visible=True
        )
        self.assertEqual(setting.user, self.user)
        self.assertEqual(setting.key, 'test_setting')
        self.assertEqual(setting.get_value(), 'test_value')
    
    def test_user_setting_boolean_type(self):
        """Test boolean setting type conversion"""
        setting = UserSetting.objects.create(
            user=self.user,
            key='bool_setting',
            value='true',
            setting_type='boolean',
            category=self.category,
            display_name='Boolean Setting'
        )
        self.assertTrue(setting.get_value())
        setting.set_value(False)
        self.assertFalse(setting.get_value())
    
    def test_user_setting_integer_type(self):
        """Test integer setting type conversion"""
        setting = UserSetting.objects.create(
            user=self.user,
            key='int_setting',
            value='42',
            setting_type='integer',
            category=self.category,
            display_name='Integer Setting'
        )
        self.assertEqual(setting.get_value(), 42)
        setting.set_value(100)
        self.assertEqual(setting.get_value(), 100)


class SystemSettingModelTest(TestCase):
    """Test SystemSetting model"""
    
    def setUp(self):
        self.admin = User.objects.create_user(
            username='admin',
            password='adminpass',
            is_staff=True
        )
        # Get or create category (may already exist from default creation)
        self.category, _ = SettingCategory.objects.get_or_create(
            name='test_system',
            defaults={
                'display_name': 'Test System',
                'is_admin_only': True
            }
        )
    
    def test_system_setting_creation(self):
        """Test SystemSetting creation"""
        setting = SystemSetting.objects.create(
            key='system_setting',
            value='system_value',
            setting_type='string',
            category=self.category,
            display_name='System Setting'
        )
        self.assertEqual(setting.key, 'system_setting')
        self.assertEqual(setting.get_value(), 'system_value')


class SettingsUtilsTest(TestCase):
    """Test settings utility functions"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.admin = User.objects.create_user(
            username='admin',
            password='adminpass',
            is_staff=True
        )
    
    def test_ensure_user_default_settings(self):
        """Test that default user settings are created"""
        from .utils import ensure_user_default_settings
        
        # Delete any existing settings (may be created by signal)
        UserSetting.objects.filter(user=self.user).delete()
        
        # Initially no settings
        self.assertEqual(UserSetting.objects.filter(user=self.user).count(), 0)
        
        # Create default settings
        ensure_user_default_settings(self.user)
        
        # Should have multiple default settings
        settings_count = UserSetting.objects.filter(user=self.user).count()
        self.assertGreater(settings_count, 0)
        
        # Check specific settings exist
        self.assertTrue(UserSetting.objects.filter(user=self.user, key='theme_preference').exists())
        self.assertTrue(UserSetting.objects.filter(user=self.user, key='show_chat_history').exists())
        self.assertTrue(UserSetting.objects.filter(user=self.user, key='response_style').exists())
        self.assertTrue(UserSetting.objects.filter(user=self.user, key='enable_weather').exists())
        self.assertFalse(UserSetting.objects.filter(user=self.user, key='language').exists())  # Should not exist
    
    def test_ensure_system_default_settings(self):
        """Test that default system settings are created"""
        from .utils import ensure_system_default_settings
        
        # Initially no system settings
        self.assertEqual(SystemSetting.objects.count(), 0)
        
        # Create default settings
        ensure_system_default_settings()
        
        # Should have multiple default settings
        settings_count = SystemSetting.objects.count()
        self.assertGreater(settings_count, 0)
        
        # Check specific settings exist
        self.assertTrue(SystemSetting.objects.filter(key='max_chat_sessions').exists())
        self.assertTrue(SystemSetting.objects.filter(key='session_retention_days').exists())
        self.assertFalse(SystemSetting.objects.filter(key='default_language').exists())  # Should not exist
    
    def test_ensure_all_default_settings_regular_user(self):
        """Test ensure_all_default_settings for regular user"""
        # Delete any existing settings (may be created by signal)
        UserSetting.objects.filter(user=self.user).delete()
        SystemSetting.objects.all().delete()
        
        # Initially no settings
        self.assertEqual(UserSetting.objects.filter(user=self.user).count(), 0)
        self.assertEqual(SystemSetting.objects.count(), 0)
        
        # Create all default settings
        ensure_all_default_settings(self.user)
        
        # Should have user settings but no system settings (not admin)
        self.assertGreater(UserSetting.objects.filter(user=self.user).count(), 0)
        self.assertEqual(SystemSetting.objects.count(), 0)
    
    def test_ensure_all_default_settings_admin(self):
        """Test ensure_all_default_settings for admin user"""
        # Delete any existing settings (may be created by signal)
        UserSetting.objects.filter(user=self.admin).delete()
        SystemSetting.objects.all().delete()
        
        # Initially no settings
        self.assertEqual(UserSetting.objects.filter(user=self.admin).count(), 0)
        self.assertEqual(SystemSetting.objects.count(), 0)
        
        # Create all default settings
        ensure_all_default_settings(self.admin)
        
        # Should have both user and system settings
        self.assertGreater(UserSetting.objects.filter(user=self.admin).count(), 0)
        self.assertGreater(SystemSetting.objects.count(), 0)


class SettingsViewsTest(TestCase):
    """Test settings views"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.admin = User.objects.create_user(
            username='admin',
            password='adminpass',
            is_staff=True
        )
        self.settings_url = reverse('settings:index')
    
    def test_settings_index_requires_login(self):
        """Test that settings page requires authentication"""
        response = self.client.get(self.settings_url)
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_settings_index_creates_defaults(self):
        """Test that accessing settings auto-creates default settings"""
        # Delete any existing settings (may be created by signal)
        UserSetting.objects.filter(user=self.user).delete()
        
        self.client.login(username='testuser', password='testpass123')
        
        # Initially no settings
        self.assertEqual(UserSetting.objects.filter(user=self.user).count(), 0)
        
        # Access settings page
        response = self.client.get(self.settings_url)
        self.assertEqual(response.status_code, 200)
        
        # Settings should now exist
        self.assertGreater(UserSetting.objects.filter(user=self.user).count(), 0)
    
    def test_settings_index_no_language_setting(self):
        """Test that language setting is not created or shown"""
        self.client.login(username='testuser', password='testpass123')
        
        # Access settings
        response = self.client.get(self.settings_url)
        self.assertEqual(response.status_code, 200)
        
        # Language setting should not exist
        self.assertFalse(UserSetting.objects.filter(user=self.user, key='language').exists())
        
        # Check JSON response doesn't include language
        json_response = self.client.get(self.settings_url + '?format=json', 
                                        HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(json_response.status_code, 200)
        data = json_response.json()
        
        # Check all settings in response
        for cat_data in data.get('settings', []):
            for setting in cat_data.get('user_settings', []):
                self.assertNotEqual(setting['key'], 'language')
    
    def test_settings_json_response(self):
        """Test JSON API response for settings modal"""
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.get(self.settings_url + '?format=json',
                                   HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertIn('settings', data)
        self.assertIn('is_admin', data)
        self.assertIsInstance(data['settings'], list)
        self.assertFalse(data['is_admin'])  # Regular user
    
    def test_settings_json_response_admin(self):
        """Test JSON API response for admin user"""
        self.client.login(username='admin', password='adminpass')
        
        response = self.client.get(self.settings_url + '?format=json',
                                   HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertTrue(data['is_admin'])  # Admin user
        
        # Should have system settings
        has_system_settings = any(
            len(cat_data.get('system_settings', [])) > 0 
            for cat_data in data['settings']
        )
        self.assertTrue(has_system_settings)
    
    def test_update_user_setting_success(self):
        """Test updating a user setting via API"""
        self.client.login(username='testuser', password='testpass123')
        
        # Ensure settings exist
        ensure_all_default_settings(self.user)
        
        # Get a setting
        setting = UserSetting.objects.filter(user=self.user).first()
        original_value = setting.get_value()
        
        # Update setting
        update_url = reverse('settings:update_user_setting')
        response = self.client.post(
            update_url,
            data={'key': setting.key, 'value': 'new_value'},
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        
        # Verify setting was updated
        setting.refresh_from_db()
        self.assertEqual(setting.get_value(), 'new_value')
    
    def test_update_user_setting_boolean(self):
        """Test updating a boolean setting"""
        self.client.login(username='testuser', password='testpass123')
        
        # Ensure settings exist
        ensure_all_default_settings(self.user)
        
        # Get boolean setting
        setting = UserSetting.objects.filter(
            user=self.user,
            setting_type='boolean'
        ).first()
        
        # Toggle the setting
        new_value = not setting.get_value()
        update_url = reverse('settings:update_user_setting')
        response = self.client.post(
            update_url,
            data={'key': setting.key, 'value': new_value},
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        setting.refresh_from_db()
        self.assertEqual(setting.get_value(), new_value)
    
    def test_update_user_setting_not_found(self):
        """Test updating non-existent setting"""
        self.client.login(username='testuser', password='testpass123')
        
        update_url = reverse('settings:update_user_setting')
        response = self.client.post(
            update_url,
            data={'key': 'non_existent_setting', 'value': 'value'},
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 404)
        data = response.json()
        self.assertIn('error', data)
    
    def test_update_system_setting_requires_admin(self):
        """Test that updating system settings requires admin"""
        self.client.login(username='testuser', password='testpass123')
        
        # Ensure system settings exist
        ensure_system_default_settings()
        
        setting = SystemSetting.objects.first()
        update_url = reverse('settings:update_system_setting')
        response = self.client.post(
            update_url,
            data={'key': setting.key, 'value': 'new_value'},
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 403)  # Forbidden
    
    def test_update_system_setting_admin_success(self):
        """Test admin updating system setting"""
        self.client.login(username='admin', password='adminpass')
        
        # Ensure system settings exist
        ensure_system_default_settings()
        
        # Get an integer setting (safer for testing)
        setting = SystemSetting.objects.filter(setting_type='integer').first()
        if not setting:
            # Fallback to any setting
            setting = SystemSetting.objects.first()
        
        # Use appropriate value based on setting type
        if setting.setting_type == 'integer':
            new_value = 100
        elif setting.setting_type == 'boolean':
            new_value = True
        else:
            new_value = 'new_system_value'
        
        # Use JSON data format
        import json
        update_url = reverse('settings:update_system_setting')
        response = self.client.post(
            update_url,
            data=json.dumps({'key': setting.key, 'value': new_value}),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200, f"Response: {response.content}")
        data = response.json()
        self.assertTrue(data['success'])
        
        # Verify setting was updated
        setting.refresh_from_db()
        self.assertEqual(setting.get_value(), new_value)
        self.assertEqual(setting.updated_by, self.admin)


class SettingsRoleBasedAccessTest(TestCase):
    """Test role-based access to settings"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.admin = User.objects.create_user(
            username='admin',
            password='adminpass',
            is_staff=True
        )
    
    def test_regular_user_sees_only_user_settings(self):
        """Test that regular users only see user settings"""
        self.client.login(username='testuser', password='testpass123')
        
        # Ensure settings exist
        ensure_all_default_settings(self.user)
        
        response = self.client.get(reverse('settings:index') + '?format=json',
                                   HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        data = response.json()
        
        # Should have user settings
        has_user_settings = any(
            len(cat_data.get('user_settings', [])) > 0 
            for cat_data in data['settings']
        )
        self.assertTrue(has_user_settings)
        
        # Should NOT have system settings
        has_system_settings = any(
            len(cat_data.get('system_settings', [])) > 0 
            for cat_data in data['settings']
        )
        self.assertFalse(has_system_settings)
    
    def test_admin_sees_both_user_and_system_settings(self):
        """Test that admin sees both user and system settings"""
        self.client.login(username='admin', password='adminpass')
        
        # Ensure settings exist
        ensure_all_default_settings(self.admin)
        
        response = self.client.get(reverse('settings:index') + '?format=json',
                                   HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        data = response.json()
        
        # Should have user settings
        has_user_settings = any(
            len(cat_data.get('user_settings', [])) > 0 
            for cat_data in data['settings']
        )
        self.assertTrue(has_user_settings)
        
        # Should also have system settings
        has_system_settings = any(
            len(cat_data.get('system_settings', [])) > 0 
            for cat_data in data['settings']
        )
        self.assertTrue(has_system_settings)


class SettingsAutoPopulationTest(TestCase):
    """Test automatic population of default settings"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
    
    def test_settings_auto_created_on_first_access(self):
        """Test that settings are auto-created when accessing settings page"""
        # Delete any existing settings (may be created by signal)
        UserSetting.objects.filter(user=self.user).delete()
        
        client = Client()
        client.login(username='testuser', password='testpass123')
        
        # No settings initially
        self.assertEqual(UserSetting.objects.filter(user=self.user).count(), 0)
        
        # Access settings
        response = client.get(reverse('settings:index'))
        self.assertEqual(response.status_code, 200)
        
        # Settings should now exist
        self.assertGreater(UserSetting.objects.filter(user=self.user).count(), 0)
    
    def test_settings_include_expected_defaults(self):
        """Test that default settings include expected items"""
        ensure_all_default_settings(self.user)
        
        # Check for expected user settings
        expected_settings = [
            'theme_preference',
            'show_chat_history',
            'response_style',
            'enable_weather',
            'auto_save_conversations',
            'email_notifications',
            'reminder_notifications',
            'policy_update_notifications'
        ]
        
        for key in expected_settings:
            self.assertTrue(
                UserSetting.objects.filter(user=self.user, key=key).exists(),
                f"Setting '{key}' should exist"
            )
        
        # Verify language setting does NOT exist
        self.assertFalse(
            UserSetting.objects.filter(user=self.user, key='language').exists(),
            "Language setting should NOT exist"
        )
    
    def test_settings_not_duplicated_on_multiple_access(self):
        """Test that settings are not duplicated when accessed multiple times"""
        client = Client()
        client.login(username='testuser', password='testpass123')
        
        # Access settings multiple times
        for _ in range(3):
            client.get(reverse('settings:index'))
        
        # Should have same number of settings (not duplicated)
        settings_count = UserSetting.objects.filter(user=self.user).count()
        
        # Access one more time
        client.get(reverse('settings:index'))
        
        # Count should be the same
        self.assertEqual(
            UserSetting.objects.filter(user=self.user).count(),
            settings_count
        )


class SettingOptionModelTest(TestCase):
    """Test SettingOption model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        # Get or create category (may already exist from default creation)
        self.category, _ = SettingCategory.objects.get_or_create(
            name='test_choice',
            defaults={
                'display_name': 'Test Choice',
                'is_user_visible': True
            }
        )
        self.setting = UserSetting.objects.create(
            user=self.user,
            key='choice_setting',
            setting_type='choice',
            category=self.category,
            display_name='Choice Setting'
        )
    
    def test_setting_option_creation(self):
        """Test SettingOption creation"""
        option = SettingOption.objects.create(
            setting=self.setting,
            value='option1',
            display_name='Option 1',
            order=1
        )
        self.assertEqual(option.setting, self.setting)
        self.assertEqual(option.value, 'option1')
        self.assertEqual(option.display_name, 'Option 1')
