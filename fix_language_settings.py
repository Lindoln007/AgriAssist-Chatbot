import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'AgriAssistant.settings')
django.setup()

from settings.models import UserSetting

# Fix: Find and delete any setting with "Language" in the name or key
print("--- CLEANING UP LANGUAGE SETTINGS ---")

# 1. Search by key (loose match)
lang_keys = UserSetting.objects.filter(key__icontains='language')
print(f"Found {lang_keys.count()} settings with 'language' in key.")
for s in lang_keys:
    print(f"Deleting ID:{s.id} Key:{s.key} Name:{s.display_name}")
    s.delete()

# 2. Search by display name
lang_names = UserSetting.objects.filter(display_name__icontains='Language')
print(f"Found {lang_names.count()} settings with 'Language' in display name.")
for s in lang_names:
    print(f"Deleting ID:{s.id} Key:{s.key} Name:{s.display_name}")
    s.delete()

print("Cleanup complete.")
