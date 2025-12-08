import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'AgriAssistant.settings')
django.setup()

from django.contrib.auth.models import User
from settings.models import UserSetting

print("--- User Settings ---")
for setting in UserSetting.objects.all():
    print(f"User: {setting.user.username} | Key: {setting.key} | Name: {setting.display_name}")
