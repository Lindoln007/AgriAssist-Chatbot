"""
Settings views with role-based access control
"""
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_http_methods
from django.contrib import messages
from django.db import transaction
from django.db.models import Q
import json
from .models import SettingCategory, UserSetting, SystemSetting, SettingOption
from .utils import ensure_all_default_settings


@login_required
def settings_index(request):
    """
    Main settings page - shows different settings based on user role
    Can return JSON for AJAX requests or HTML for full page
    Automatically creates default settings if they don't exist
    """
    # Ensure all default settings exist for this user
    ensure_all_default_settings(request.user)
    
    # Remove any language settings that might exist (cleanup)
    UserSetting.objects.filter(user=request.user, key='language').delete()
    SystemSetting.objects.filter(key='default_language').delete()
    
    # Get visible categories based on user role
    is_admin = request.user.is_staff or request.user.is_superuser
    
    if is_admin:
        categories = SettingCategory.objects.filter(
            Q(is_admin_only=True) | Q(is_user_visible=True)
        ).distinct()
    else:
        categories = SettingCategory.objects.filter(
            is_user_visible=True,
            is_admin_only=False
        )
    
    categories = categories.order_by('order', 'name')
    
    # Build category data with settings (exclude language settings)
    category_data = []
    for category in categories:
        user_settings = UserSetting.objects.filter(
            user=request.user,
            category=category,
            is_visible=True
        ).exclude(key='language').order_by('order', 'display_name')
        
        system_settings = []
        if is_admin:
            system_settings = list(SystemSetting.objects.filter(
                category=category
            ).exclude(key='default_language').order_by('order', 'display_name'))
        
        if user_settings.exists() or system_settings:
            category_data.append({
                'category': category,
                'user_settings': list(user_settings),
                'system_settings': system_settings,
            })
    
    context = {
        'category_data': category_data,
        'is_admin': is_admin,
    }
    
    # Check if this is an AJAX request for modal content
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.GET.get('format') == 'json':
        # Return JSON data for AJAX
        settings_json = []
        for cat_data in category_data:
            category_settings = {
                'category': {
                    'id': cat_data['category'].id,
                    'name': cat_data['category'].name,
                    'display_name': cat_data['category'].display_name,
                    'description': cat_data['category'].description,
                    'icon': cat_data['category'].icon,
                    'is_admin_only': cat_data['category'].is_admin_only,
                },
                'user_settings': [],
                'system_settings': []
            }
            
            for setting in cat_data['user_settings']:
                # Explicitly skip language settings
                if setting.key == 'language':
                    continue
                category_settings['user_settings'].append({
                    'key': setting.key,
                    'display_name': setting.display_name,
                    'description': setting.description,
                    'setting_type': setting.setting_type,
                    'value': setting.get_value(),
                    'options': [{'value': opt.value, 'display_name': opt.display_name} for opt in setting.options.all()]
                })
            
            for setting in cat_data['system_settings']:
                # Explicitly skip language settings
                if setting.key == 'default_language':
                    continue
                category_settings['system_settings'].append({
                    'key': setting.key,
                    'display_name': setting.display_name,
                    'description': setting.description,
                    'setting_type': setting.setting_type,
                    'value': setting.get_value(),
                    'options': [{'value': opt.value, 'display_name': opt.display_name} for opt in setting.options.all()]
                })
            
            settings_json.append(category_settings)
        
        return JsonResponse({
            'settings': settings_json,
            'is_admin': is_admin
        })
    
    return render(request, 'settings/index.html', context)


@login_required
@require_POST
def update_user_setting(request):
    """
    Update a user setting via AJAX
    """
    try:
        data = json.loads(request.body)
        setting_key = data.get('key')
        new_value = data.get('value')
        
        if not setting_key:
            return JsonResponse({'error': 'Setting key is required'}, status=400)
        
        try:
            setting = UserSetting.objects.get(user=request.user, key=setting_key, is_visible=True)
        except UserSetting.DoesNotExist:
            return JsonResponse({'error': 'Setting not found'}, status=404)
        
        # Validate and set value
        setting.set_value(new_value)
        setting.save()
        
        return JsonResponse({
            'success': True,
            'message': f'{setting.display_name} updated successfully',
            'value': setting.get_value()
        })
    
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_POST
def update_system_setting(request):
    """
    Update a system setting (admin only) via AJAX
    """
    if not (request.user.is_staff or request.user.is_superuser):
        return JsonResponse({'error': 'Admin access required'}, status=403)
    
    try:
        data = json.loads(request.body)
        setting_key = data.get('key')
        new_value = data.get('value')
        
        if not setting_key:
            return JsonResponse({'error': 'Setting key is required'}, status=400)
        
        try:
            setting = SystemSetting.objects.get(key=setting_key)
        except SystemSetting.DoesNotExist:
            return JsonResponse({'error': 'Setting not found'}, status=404)
        
        # Validate and set value
        setting.set_value(new_value)
        setting.updated_by = request.user
        setting.save()
        
        return JsonResponse({
            'success': True,
            'message': f'{setting.display_name} updated successfully',
            'value': setting.get_value()
        })
    
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def get_setting_value(request, setting_type, setting_key):
    """
    Get current value of a setting (for real-time updates)
    """
    try:
        if setting_type == 'user':
            setting = UserSetting.objects.get(user=request.user, key=setting_key, is_visible=True)
        elif setting_type == 'system':
            if not (request.user.is_staff or request.user.is_superuser):
                return JsonResponse({'error': 'Admin access required'}, status=403)
            setting = SystemSetting.objects.get(key=setting_key)
        else:
            return JsonResponse({'error': 'Invalid setting type'}, status=400)
        
        return JsonResponse({
            'key': setting.key,
            'value': setting.get_value(),
            'display_name': setting.display_name
        })
    
    except (UserSetting.DoesNotExist, SystemSetting.DoesNotExist):
        return JsonResponse({'error': 'Setting not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
