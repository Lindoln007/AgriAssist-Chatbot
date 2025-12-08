import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'AgriAssistant.settings')
django.setup()

from settings.models import UserSetting, SystemSetting, SettingCategory

print("--- ALL USER SETTINGS ---")
for s in UserSetting.objects.all():
    print(f"ID: {s.id} | User: {s.user.username} | Key: '{s.key}' | Display: '{s.display_name}' | Cat: {s.category.name if s.category else 'None'}")

print("\n--- ALL SYSTEM SETTINGS ---")
for s in SystemSetting.objects.all():
    print(f"ID: {s.id} | Key: '{s.key}' | Display: '{s.display_name}'")

print("\n--- CATEGORIES ---")
for c in SettingCategory.objects.all():
    print(f"Cat: {c.name} (Display: {c.display_name})")
